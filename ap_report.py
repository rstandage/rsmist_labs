#!/usr/bin/env python3

'''

This script gets information on all APs within an org and provides a .csv file

***Turn off the get_config by setting to zero if AP count is above 5k or you dont want to see SSIDs/BSSIDs***

'''

import json, requests, time, os
from dotenv import load_dotenv
from datetime import date, datetime
import pandas as pd

load_dotenv()

api_token = os.getenv("API_TOKEN") #change ito a string if needed
org_id = os.getenv("ORG_ID") #change ito a string if needed
limit = 1000 #Modify the amount of items that are pulled back at a time
output_location = "" #Set location for reports to be stored

# Create URLs
base_url = os.getenv("BASE_URL") #change ito a string if needed
org_aps_url = '{}/orgs/{}/devices/search?limit={}'.format(base_url, org_id, limit)
org_sites_url = '{}/orgs/{}/sites'.format(base_url, org_id)




# define standard headers
mist_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

mist_api_count = 0
count = 0
Data_Array = []
get_config = 1 #this will also collect the BSSIDs from the APs
#Need to make change to enable this to scale. Pull back all APs and create an Array rather than one at a time

############################################################

def create_site_array(url):
 #Creates Array of item names and IDs and country code for sites.
    global mist_api_count
    Array=[]
    resp0 = requests.get(url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data = json.loads(resp0.text)
    for i in data:
        site = {
        'id': i.get('id'),
        'name': i.get('name'),
        'cc': i.get('country_code')
        }
        Array.append(site)
    return Array
 
def find_site_details(id, Site_Array):
    name = ''
    cc = ''
    for s in Site_Array:
        if s.get('id') == id:
            name = s.get('name')
            cc = s.get('cc')
            break
    return name, cc

def get_inital_results(url):
#function to get the initial data and add to the array. also returns total and the 'next'
    global mist_api_count
    global count
    global Data_Array
    resp = requests.get(url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data = json.loads(resp.text)
    for i in data.get('results'):
        Data_Array.append(i)
    count += len(data.get('results'))
    total = data.get('total')
    nexturl = data.get('next')
    return total, nexturl


def get_next_results(nexturl):
#function to get the data and add to the array. also returns the 'next'
    global mist_api_count
    global count
    global Data_Array 
    try:
        url = base_url+(nexturl.replace('api/v1/', ''))
        resp = requests.get(url, headers=mist_headers)
        mist_api_count = mist_api_count+1
        data = json.loads(resp.text)
        for i in data.get('results'):
            Data_Array.append(i)
        count += len(data.get('results'))
        nexturl = data.get('next')
        return nexturl
    except Exception as e:
        print("An error occurred: {}".format(e))
        print("failed at count {}".format(count))
        print("next url was: {}".format(nexturl))
        return None 

def get_ap_config(siteid, mac):
    #uses the mac address to get BSSIDs (increases API count to 1 per AP)
    global mist_api_count
    url = '{}/sites/{}/devices/last_config/search?ap={}'.format(base_url, siteid, mac)
    resp = requests.get(url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data = json.loads(resp.text)
    results = data.get('results')
    for i in results:
        bssid_list = i.get('radio_macs')
        ssid_list = i.get('ssids')
    return bssid_list, ssid_list

def format_data(Data_Array, Site_Array):
    New_Array = []
    for ap in Data_Array:
        site_id = ap.get('site_id')
        site_name, site_cc = find_site_details(site_id, Site_Array)
        mac = ap.get('mac')
        if get_config == 1:
            bssid_list, ssid_list = get_ap_config(site_id, mac)
        else:
            bssid_list = []
            ssid_list = []
        data = {
        'Name':ap.get('last_hostname'),
        'Site':site_name,
        'MAC':mac,
        'IP':ap.get('ip'),
        'Country Code': site_cc,
        'Type':ap.get('sku'),
        'Firmware':ap.get('version'),
        'Port Speed':ap.get('eth0_port_speed'),
        'LLDP System Name':ap.get('lldp_system_name'),
        'LLDP Port':ap.get('lldp_port_id'),
        'LLDP System Description':ap.get('lldp_system_desc'),
        'SSIDS':ssid_list,
        'BSSIDs':bssid_list,
        '2.4Ghz Power':ap.get('band_24_power'),
        '2.4Ghz Bandwidth':ap.get('band_24_bandwith'),
        '2.4Ghz Channel':ap.get('band_24_channel'),
        '5Ghz Power':ap.get('band_5_power'),
        '5Ghz Bandwidth':ap.get('band_5_bandwith'),
        '5Ghz Channel':ap.get('band_5_channel'),
        }
        New_Array.append(data)
    return New_Array

############################################################

def main():
    global mist_api_count
    global count
    global Data_Array
    Site_Array = create_site_array(org_sites_url)
    total, nexturl = get_inital_results(org_aps_url)
    print ("Creating Data for {} Access Points".format(total))
    while count is not total:
        if nexturl is not None:
            nexturl = get_next_results(nexturl)
        else:
            print("Completed Data Collection")
            break
    print ("Formatting Data for {}".format(len(Data_Array)))
    Device_Data = format_data(Data_Array, Site_Array)
    df = pd.DataFrame(Device_Data)        
    new_file = '{}AP_Report_{}.csv'.format(output_location,date.today())
    print (f"\nCreated Report:", new_file)
    print ("Mist API Calls: {}".format(mist_api_count))
    df.to_csv(new_file, index=False)

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
