#!/usr/bin/env python3

'''
Creates a new site based on set user input
3 subnets are requetsed and subnetted to create network variables
Hard set items are the "branch" rf template and variable details

'''

import json, requests
import time
import os
from dotenv import load_dotenv
from ipaddress import IPv4Network
from ipaddress import IPv4Address

#Add path to .env file or specify variables below
load_dotenv()

mist_api_token = os.getenv("API_TOKEN")
google_api_token = os.getenv("GOOGLE_API_TOKEN")
org_id = os.getenv("ORG_ID")

# Create URLs
base_url = os.getenv("BASE_URL")
org_url = "{}/orgs".format(base_url)
google_geolocation_url = "https://maps.googleapis.com/maps/api/geocode/json"
org_sites_url = "{}/orgs/{}/sites".format(base_url, org_id)
org_sitegroups_url = '{}/orgs/{}/sitegroups'.format(base_url, org_id)
org_rftemplates_url = '{}/orgs/{}/rftemplates'.format(base_url, org_id)

# define standard headers
mist_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token {}'.format(mist_api_token)
    }

#Create Global Variables
mist_api_count = 0
google_api_count = 0
sitegroups_dict = {}
rftemplates_dict = {}

debug = 0

############################################################

def get_user_input():
#gets input from user
    print (f"This script will build a new site to org preset in environment variables \nPlease enter details below\n")
    input1 = input("Site Name (no spaces, max 16 characters):")
    input2 = input("Enter Site ID: ")
    input3 = input("Enter Site Address: ")
    input4 = input("Enter Site Types in a list (e.g. uk retail hub: ")
    input5 = input("Enter Subnet 1 (e.g 10.172.0.0/23): ")
    input6 = input("Enter Subnet 2 (e.g 10.172.2.0/23): ")
    input7 = input("Enter Subnet 3 (e.g 10.172.4.0/23): ")
    input("\nHit Return to Begin, crtl^c to cancel at any time  ")
    return input1, input2, input3, input4, input5, input6, input7

def check_user_variables(sitename,siteid,siteaddr,sitegroups,sitenet1,sitenet2,sitenet3):
    variables = [sitename,siteid,siteaddr,sitegroups,sitenet1,sitenet2,sitenet3]
    for var in variables:
        if var == "":
            raise ValueError(f"\n Input is missing from user variables.")

def POST_to_mist(x, y):
#Sends data to mist where x is the url and y is the payload as a dict or array
    global mist_api_count
    payload = json.dumps(y)
    send = requests.request("POST", x, data=payload, headers=mist_headers)
    mist_api_count = mist_api_count+1
    text = json.loads(send.text)
    if send.status_code == 200:
        response = True
    else:
        print("Failed - HTTP Error {}".format(send.status_code))
        response = False
    return response, text

def PUT_to_mist(x, y):
#Sends data to mist where x is the url and y is the payload as a dict or array
    global mist_api_count
    payload = json.dumps(y)
    send = requests.request("PUT", x, data=payload, headers=mist_headers)
    mist_api_count = mist_api_count+1
    text = json.loads(send.text)
    if send.status_code == 200:
        response = True
    else:
        print("Failed - HTTP Error {}".format(send.status_code))
        response = False
    return response, text

def get_sitegroups():
#Creates dictionary of pre-existing site groups (id as key)
    global mist_api_count
    global sitegroups_dict
    resp0 = requests.get(org_sitegroups_url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        sitegroups_dict[i['id']] = i['name']

def get_rftemplates():
#Creates dictionary of pre-existing rf templates (name as key)
    global mist_api_count
    global rftemplates_dict
    resp0 = requests.get(org_rftemplates_url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        rftemplates_dict[i['name']] = i['id']

def get_google_geolocation(x):
#Gets address details from google APIs
    global google_api_count
    global loc_error_sites
    lat, lng, cc, fa = None, None, None, None
    api_url = "{}?address={}&key={}".format(google_geolocation_url, x, google_api_token)
    resp = requests.get(api_url)
    google_api_count = google_api_count+1
    if resp.status_code != 200:
        return None, None, None, None
    try:
        r = json.loads(resp.text)
        results = r['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
        for i in results['address_components']:
            if 'country' in i.get('types'):
                cc = i.get('short_name')
        fa = results.get('formatted_address')
    except (KeyError, AttributeError, IndexError) as error: 
        print("***Failed {} for {} ***".format(error, x))
        loc_error_sites.append(x)
    return lat, lng, cc, fa

def create_sitegroups(x):
#Looks for new site groups in input data and validates against existing config. New groups are created and returned with an ID 
    global sitegroups_dict
    global mist_api_count
    grouplist = []
    sitegrouplist = x.split()
    for g in sitegrouplist:
        if g not in sitegroups_dict.values() and g not in grouplist:
            grouplist.append(g)
    if grouplist == []:
        print (" No new groups to create... skipping")
    else:
        for i in grouplist:
            data = {
            'name': i
            }
            result, resp = POST_to_mist(org_sitegroups_url, data)
            print('Creating new group  - [{}]\t {}'.format(i, result))
            group_id = resp.get("id")
            sitegroups_dict[group_id] = i

def convert_sitegroups(x, y):
#Converts group names to a list of IDs 
    namelist = []
    if x is None:
        namelist = ['None']
    else:
        for i in x:
            for gid, gname in y.items():
                if i == gname:
                    namelist.append(gid)
    return namelist

def searcharray(x, y):
#Searches for seq number and returns corresponding dict values
    return [element for element in y if element['Seq'] == x]

def create_site_config(w, x, y, z):
#Gets Data, creates a dictionary with all site data and tidies up naming convention
    global sitegroups_dict
    global rftemplates_dict
    print ("Creating Site Data for {}".format(x+"-"+w))    
    sitegroupnames = z.split()
    groupidlist = convert_sitegroups(sitegroupnames, sitegroups_dict)
    lat, lng, cc, fa = get_google_geolocation(y)
    if "branch" in sitegroupnames:
        rftemplate = rftemplates_dict.get("branchrftemplate")
    elif "dc" in sitegroupnames:
        rftemplate = rftemplates_dict.get("dcrftemplate")
    else:
        rftemplate = rftemplates_dict.get("default")
    data = {
    'name': x+"-"+w,
    'address': fa,
    'alarmtemplate_id': 'null',
    "rftemplate_id": rftemplate,
    "country_code": cc,
    "timezone": "Europe/London",
    "sitegroup_ids": groupidlist,
    "latlng": {
       "lat": lat,
       "lng": lng
       }
    }
    return data

def create_subnets(x, y):
# Takes a network (x) and breaks it down into smaller subnets with (y) CIDR. Returns an array with network strings
    Net_Array = []
    count = 0
    supernet = IPv4Network(x)
    for n in supernet.subnets(new_prefix = y):
        count = count+1
        data = {
        "Seq": count,
        "Network": str(n),
        "First Host": str(n[1]),
        "Last Host": str(n[-2]),
        "Broadcast": str(n[-1])
        }
        Net_Array.append(data)
    print("Created {} subnets from {} as /{}s".format(count,x, y))
    return Net_Array

def create_variables(x,y,z):
#Creates data dict for variables. items are related to subnet arrays
     data = {
     "vars": {
         "corp_vlan" : "100",
         "corp_net": (searcharray(1, x)[0]).get('Network'),
         "corp_gw": (searcharray(1, x)[0]).get('Last Host'),    
         "guest_vlan": "120",
         "guest_net": (searcharray(4, y)[0]).get('Network'),
         "guest_gw": (searcharray(4, y)[0]).get('Last Host'),
         "boyd_vlan": "140",
         "byod_net": (searcharray(5, y)[0]).get('Network'),
         "byod_gw": (searcharray(5, y)[0]).get('Last Host'),
         "mgmt_vlan": "150",
         "mgmt_net": (searcharray(1, z)[0]).get('Network'),
         "mgmt_gw": (searcharray(1, z)[0]).get('Last Host'),
         },
    "auto_upgrade": {
        "enabled": True,
        "version": "custom",
        "time_of_day": "02:00",
        "custom_versions": {
            "AP33": "0.10.24516"
        },
        "day_of_week": "sun"
        }

     }
     return data

############################################################

def main():
    global mist_api_count
    global google_api_count
    try:
        sitename,siteid,siteaddr,sitegroups,sitenet1,sitenet2,sitenet3 = get_user_input()
        check_user_variables(sitename,siteid,siteaddr,sitegroups,sitenet1,sitenet2,sitenet3)
        start_time = time.time()
        #Create Site Groups
        get_sitegroups()
        get_rftemplates()
        print (f"\nStep 1 - Create Site Groups...") 
        create_sitegroups(sitegroups)
        #Create Sites
        print (f"\nStep 2 - Build Site...")
        site_data = create_site_config(sitename,siteid,siteaddr,sitegroups)      
        resp, text = POST_to_mist(org_sites_url, site_data)
        if resp is False:
            print(f"\nFailed to post data")
            print(text)
        else:
            site_id= text.get("id")
            print ("Site ID {} successfully created".format(site_id))       
        #Create subnets
        print (f"\nStep 3 - Do some Subnetting...")
        Net1_Array = create_subnets(sitenet1, 24)
        Net2_Array = create_subnets(sitenet2, 23)
        Net3_Array = create_subnets(sitenet3, 25)
        #Create Variables
        print (f"\nStep 4 - Create Variables...")
        site_vars = create_variables(Net1_Array,Net2_Array,Net3_Array)
        site_vars != {}
        #Send variables to cloud
        print (f"\nStep 5 - Send variables to cloud...")
        site_url = "{}/sites/{}/setting".format(base_url, site_id)
        response, text = PUT_to_mist(site_url, site_vars)
        print (response)
        print(f"\nGoogle API count: ", google_api_count)
        print(f"\nMist API count: ", mist_api_count)
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
    except KeyboardInterrupt:
        print("Cancelled By User")  

def check_env_variables():
    variables = ["API_TOKEN", "GOOGLE_API_TOKEN", "ORG_ID", "BASE_URL"]
    for var in variables:
        if not os.getenv(var):
            raise ValueError(f"\n {var} is missing from environment variables.")

############################################################

if __name__ == '__main__':
# Ensure variables are defined
    check_env_variables()
    main() 
