#!/usr/bin/env python3

'''
This script gathers config data from WLAN templates and generates a report

You will need to add a full path for output_location

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
org_wlans_url = '{}/orgs/{}/wlans'.format(base_url, org_id)
tunnels_url = '{}/orgs/{}/mxtunnels'.format(base_url, org_id)
template_url = '{}/orgs/{}/templates'.format(base_url, org_id)
org_sitegroups_url = '{}/orgs/{}/sitegroups'.format(base_url, org_id)

#Set location for reports to be stored
output_location = ""

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

api_count = 0
WLAN_Array = []
Template_Array = []
tunneldict = {}
sitegroupdict = {}

############################################################


def get_tunnels():
    global api_count
    global tunneldict
    resp0 = requests.get(
       tunnels_url, 
       headers=headers)       
    api_count = api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        tunneldict[i['id']] = i['name']  

def get_templates():
    global api_count
    global Template_Array
    templatedict = {}
    resp1 = requests.get(
       template_url, 
       headers=headers)       
    api_count = api_count+1
    data1 = json.loads(resp1.text)
    for i in data1:
        templatedict = {
        'id': i['id'],
        'name': i['name'],
        'applies_to': i['applies']['sitegroup_ids'] 
        }
        Template_Array.append(templatedict)

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

def convert_tunnel_ids(x, y):
    for tid, tname in y.items():
        if tid == x:
            tunnelname = tname
        else:
            tunnelname = "none"
    return tunnelname

def convert_template_ids(x, y):
    for temp in y:
        if x == temp['id']:
            tempname = temp['name']
    return tempname

def convert_sitegroup_ids(x, y):
    groupnamelist = []
    for i in x:
        for gid, gname in y.items():
            if i == gid:
                groupnamelist.append(gname)
    return groupnamelist

def create_applies_to(x, y):
    for temp in y:
        if x == temp['id']:
            appliesto = temp['applies_to']
    return appliesto

def format_data(x):
# Format data and set required values
    
    ssid = x['ssid']
    id = x['id']
    enabled = str(x['enabled'])
    modifiedtime = str(datetime.fromtimestamp(x['modified_time']))
    authservers = []
    for server in x['auth_servers']:
        authservers.append(server['host'])
    acctservers = []
    for server in x['acct_servers']:
        acctservers.append(server['host'])    
    if x['radsec']['enabled'] == True and x['radsec']['use_mxedge'] == True:
        radsec = "Use Mist Edge"
    else:
        radsec = "None"
    mxtunnel_id = x['mxtunnel_id']
#    mxtunnel_name = convert_tunnel_ids(mxtunnel_id, tunneldict)
    vlan_id = x['vlan_id']
    authtype = x['auth']['type']
    templateid = x['template_id']
    templatename = convert_template_ids(templateid, Template_Array)
    templateappliesto_id = create_applies_to(templateid, Template_Array)
    templateappliesto_name = convert_sitegroup_ids(templateappliesto_id, sitegroupdict)

    #Set columns for each site
    values = {
    'SSID': ssid,
    'ID': id,
    'Enabled': enabled,
    'Last Modified': modifiedtime,
    'VLAN': vlan_id,
    'Authentication Type': authtype,
    'Authentication Servers': authservers,
    'Accounting Servers': acctservers,
    'RadSec': radsec,
#    'Edge Tunnel': mxtunnel_name,
    'Template Name': templatename,
    'Template Applies To': templateappliesto_name
    }
    return values    


def get_wlan_data():
#Get WLAN Template Settings and create Array

    global api_count
    global Site_Array
    sites_dict = {}
    #Get Org site data
    resp2 = requests.get(
        org_wlans_url, 
        headers=headers)
    api_count = api_count+1
    data2 = json.loads(resp2.text)
    for wlan in data2:
        wlan_data = format_data(wlan)
        WLAN_Array.append(wlan_data)   


def main():
        start_time = time.time()
        print(f"** Polling For WLAN Config...**")
        get_tunnels()
        get_templates()
        get_sitegroups()
        get_wlan_data()
#        print(json.dumps(WLAN_Array, indent=2))
        df = pandas.DataFrame(WLAN_Array)        
        new_file = '{}/wlan_template_report_{}.csv'.format(output_location, date.today())
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