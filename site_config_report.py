#!/usr/bin/env python3

'''


This script gathers data on all sites for compliance verification adn creates a CSV file. You will need to add a full path for output_location

'''

import json, requests
import pandas
import time
import os
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

# Create URLs
base_url = os.getenv("BASE_URL")
org_site_list = '{}/orgs/{}/sites'.format(base_url, org_id)
org_sitegroups_url = '{}/orgs/{}/sitegroups'.format(base_url, org_id)
rftemplates_url = '{}/orgs/{}/rftemplates'.format(base_url, org_id)
alarmtemplates_url = '{}/orgs/{}/alarmtemplates'.format(base_url, org_id)

#Set location for reports to be stored
output_location = ""

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

api_count = 0
Site_Array = []
sitegroupdict = {}
rftemplatedict = {}
alarmtemplatedict = {}
############################################################
def convert_ids_list(x, y):
    namelist = []
    for i in x:
        for gid, gname in y.items():
            if i == gid:
                namelist.append(gname)
    return namelist

def convert_ids_str(x, y):
    namestr = ""
    for i, n in y.items():
        if x == i:
            namestr = n
    return namestr

def get_rftemplate():
    global api_count
    global rftemplatedict
    resp0 = requests.get(
       rftemplates_url, 
       headers=headers)       
    api_count = api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        rftemplatedict[i['id']] = i['name']         

def get_alarmtemplate():
    global api_count
    global alarmtemplatedict
    resp0 = requests.get(
       alarmtemplates_url, 
       headers=headers)       
    api_count = api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        alarmtemplatedict[i['id']] = i['name'] 

def format_data(x, y):
# Merges both dictionaries and extracts correct data for each site
    for i in x:
        for j, k in y.items():
            if k == i['id']:
                sitedata = i
    y.update(sitedata)

    address = y['address']
    timezone = y['timezone']
    sitegroupsid = y['sitegroup_ids']
    sitegroupname = convert_ids_list(sitegroupsid, sitegroupdict)
    rftemplateid = y['rftemplate_id']
    rftemplatename = convert_ids_str(rftemplateid, rftemplatedict)
    sitemodifiedtime = str(datetime.fromtimestamp(y['modified_time']))
    alarmtemplateid = y['alarmtemplate_id']
    alarmtemplatename = convert_ids_str(alarmtemplateid, alarmtemplatedict)
    upgrade = y['auto_upgrade']['enabled']
    version = y['auto_upgrade']['version']
    if 'proxy' in y:
        proxy = y['proxy']['url']
    else:
        proxy = 'none'

    #Set columns for each site
    values = {
    'Address': address,
    'Time Zone': timezone,
    'Last Modified': sitemodifiedtime,
    'Site Groups': sitegroupname,
    'Auto Upgrade': upgrade,
    'Version': version,
    'Site Proxy': proxy,
    'RF Template': rftemplatename,
    'Alarm Template': alarmtemplatename

    }
    return values    
 
def get_sitegroups():
    global api_count
    global sitegroupdict
    resp0 = requests.get(
       org_sitegroups_url, 
       headers=headers)       
    api_count = api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        sitegroupdict[i['id']] = i['name']                  

def get_data():
#Get setting for each site

    global api_count
    global Site_Array
    global sitegroupdict
    sites_dict = {}
    #Get Org site data
    resp1 = requests.get(
        org_site_list, 
        headers=headers)
    api_count = api_count+1
    data1 = json.loads(resp1.text)
    for i in data1:
        sites_dict[i['name']] = i['id']

    # Get settings from each site
    for site_name, site_id in sites_dict.items():
        site_config_url = '{}/sites/{}/setting'.format(base_url, site_id)
        resp2 = requests.get(
            site_config_url, 
            headers=headers )
        api_count = api_count+1
        data2 = json.loads(resp2.text)
        site_data = {'Site Name': site_name, ' Site ID': site_id,}
        site_data.update(format_data(data1, data2))
        Site_Array.append(site_data)


def main():
        start_time = time.time()
        print(f"** Polling For Site Details...**")
        get_sitegroups()
        get_rftemplate()
        get_alarmtemplate()
        get_data()
#        print(json.dumps(Site_Array, indent=2))
        df = pandas.DataFrame(Site_Array)        
        new_file = '{}/site_template_report_{}.csv'.format(output_location, date.today())
        print (f"\nCreated Report:", new_file)
        df.to_csv(new_file)
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)  

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == '' or output_location == '' or base_url == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
        print('base_url={}'.format(base_url))
        print('output_location={}'.format(output_location))
    else:  
        main()  