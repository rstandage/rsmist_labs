#!/usr/bin/env python3

'''

This script gathers org, site and WLAN template information and creates an .xlsx file

'''

import json, requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

#Set location for reports to be stored
output_location = ("")

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

# Create URLs
base_url = os.getenv("BASE_URL")
org_uri = "{}/orgs/{}".format(base_url, org_id)

#Index names
org_sites = 'sites'
org_sitegroups = 'sitegroups'
rftemplates = 'rftemplates'
alarmtemplates = 'alarmtemplates'
org_wlans = 'wlans'
tunnels = 'mxtunnels'
org_templates = 'templates'
org_config = 'setting'
org_admins = 'admins'

#Create URLs
org_sites_url = '{}/{}'.format(org_uri, org_sites)
org_sitegroups_url = '{}/{}'.format(org_uri, org_sitegroups)
rftemplates_url = '{}/{}'.format(org_uri, rftemplates)
alarmtemplates_url = '{}/{}'.format(org_uri, alarmtemplates)
org_wlans_url = '{}/{}'.format(org_uri, org_wlans)
tunnels_url = '{}/{}'.format(org_uri, tunnels)
template_url = '{}/{}'.format(org_uri, org_templates)
org_config_url = '{}/{}'.format(org_uri, org_config)
org_admins_url = '{}/{}'.format(org_uri, org_admins)

url_dict = {
    org_sites : org_sites_url,
    org_sitegroups : org_sitegroups_url,
    rftemplates : rftemplates_url,
    alarmtemplates : alarmtemplates_url,
    org_wlans : org_wlans_url,
    tunnels : tunnels_url,
    org_templates : template_url,
    org_config : org_config_url,
    org_admins : org_admins_url
    }

# define standard headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token {}'.format(api_token)
    }

#Create Global Variables
api_count = 0
Data_Array = []
Site_Array = []
Org_Array = []
WLAN_Array = []


############################################################
# Functions to Get data

def get_all_org_data():
#Get all data for reports. Run initially
   global api_count
   global Data_Array
   print("Getting Org Data")
   for key, url in url_dict.items():
        try:
            newdict = {}
            resp = requests.get(url, headers=headers)
            api_count = api_count+1
            print(".")
            data = json.loads(resp.text)
            newdict[key] = data
            Data_Array.append(newdict)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)

def get_all_site_data(x):
#Run from within the format_site_data function as it could be a lot of API calls
    global api_count
    Array = []
    print("Getting Site Data")
    for site_id, site_name in x.items():
        sitedict = {}
        try:
            site_config_url = '{}/sites/{}/setting'.format(base_url, site_id)
            resp = requests.get(site_config_url, headers=headers )
            api_count = api_count+1
            print(".")
            data = json.loads(resp.text)
            sitedict[site_name] = data
            Array.append(sitedict)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)
    return Array        

############################################################
# Functions to Format Data

def get_data(x, y):
#get the correct data from full Array where y is index name
    dataset = []
    for i in x:
        for name, data in  i.items():
            if name == y:
                dataset = data
    return dataset


def count_values(x):
    count = 0
    for i in x:
        count = count+1
    return count


def convert_ids_str(x, y):
    namestr = ""
    for i, n in y.items():
        if x == i:
            namestr = n
    return namestr


def create_id_name_dict(x):
    datadict = {}
    for i in x:
        datadict[i.get('id')] = i.get('name')
    return datadict


def create_template_array(x):
    Array = []
    for i in x:
        datadict = {
        'id': i.get('id'),
        'name': i.get('name'),
        'applies_to': i.get('applies', {}).get('sitegroup_ids') 
        }
        Array.append(datadict)
    return Array 


def convert_template_ids(x, y):
    for temp in y:
        if x == temp['id']:
            tempname = temp['name']
    return tempname


def convert_ids_list(x, y):
    namelist = []
    if x is None:
        namelist = 'None'
    else:
        for i in x:
            for gid, gname in y.items():
                if i == gid:
                    namelist.append(gname)
    return namelist


def create_applies_to(x, y):
    for temp in y:
        if x == temp.get('id'):
            appliesto = temp.get('applies_to')
    return appliesto   

def merge_data(x, y):   
# Merges both data arrays matched on ID
    New_Array = []
    for i in x:
        for j in y:
            for name, data in j.items():
                sitedict = {}
                if i['id'] == data.get('site_id'):
                    alldata = data
                    alldata.update(i)
                    sitedict[name] = alldata
                    New_Array.append(sitedict)
    return New_Array

############################################################
# Build Reports

def format_org_report():
    #Create data array for org report
    global Org_Array
    org_data = get_data(Data_Array, org_config)
    admin_data = get_data(Data_Array, org_admins)
    sites = get_data(Data_Array, org_sites)
    permitted_users = []
    nonpermitted_users = []
    org_id = org_data.get('org_id')
    site_count = count_values(sites)
    pwpolicyenabled = str(org_data.get('password_policy', {}).get('enabled'))
    pwpolicylength = org_data.get('password_policy', {}).get('min_length')
    for a in admin_data:
        adminid = a.get('admin_id')
        adminemail = a.get('email')
        for r in a.get('privileges'):
                role = r.get('role')
        adminname = ("{} {} - {}".format(a.get('first_name'), a.get('last_name'), role))
        if adminid == '' or adminid == '': #Add permitted Users
                userpermitted = 'Yes'
                permitted_users.append(adminname)
        else:
                userpermitted = 'No'
                nonpermitted_users.append(adminname)
    timeoutpolicy = org_data.get('ui_idle_timeout')
    modifiedtime = str(datetime.fromtimestamp(org_data.get('modified_time')))
    #Set Columns for ORG
    values = {
    'Org Id': org_id,
    'Total Sites': site_count,
    'Password Policy': pwpolicyenabled,
    'Password Length': pwpolicylength,
    'UI Idle Timeout': timeoutpolicy,
    'Permitted Users': permitted_users,
    'Non Permitted Users': nonpermitted_users,
    'Last Modified': modifiedtime
    }
    Org_Array.append(values)


def format_wlan_report():
    #Create data array for WLAN report
    wlan_data = get_data(Data_Array, org_wlans)
    tunneldict = create_id_name_dict(get_data(Data_Array, tunnels))
    Template_Array = create_template_array(get_data(Data_Array, org_templates))
    sitegroupdict = create_id_name_dict(get_data(Data_Array, org_sitegroups))
    count = count_values(wlan_data)
    for wlan in wlan_data:
        ssid = wlan.get('ssid')
        id = wlan.get('id')
        enabled = str(wlan.get('enabled'))
        modifiedtime = str(datetime.fromtimestamp(wlan.get('modified_time')))
        authservers = []
        for server in wlan.get('auth_servers'):
            authservers.append(server.get('host'))
        acctservers = []
        for server in wlan.get('acct_servers'):
            acctservers.append(server.get('host'))    
        if wlan['radsec']['enabled'] == True and wlan['radsec']['use_mxedge'] == True:
            radsec = "Use Mist Edge"
        else:
            radsec = "None"
        mxtunnel_id = wlan.get('mxtunnel_id')
        if mxtunnel_id == "null":
            mxtunnel_name = "none"
        else:
            mxtunnel_name = convert_ids_str(mxtunnel_id, tunneldict)
        vlan_id = wlan.get('vlan_id')
        authtype = wlan.get('auth', {}).get('type')
        templateid = wlan.get('template_id')
        templatename = convert_template_ids(templateid, Template_Array)
        templateappliesto_id = create_applies_to(templateid, Template_Array)
        templateappliesto_name = convert_ids_list(templateappliesto_id, sitegroupdict)
        
        #Set columns for each WLAN
        values = {
        'Template Name': templatename,
        'Template ID' : templateid,
        'Template Applies To': templateappliesto_name,
        'SSID': ssid,
        'ID': id,
        'Enabled': enabled,
        'VLAN': vlan_id,
        'Authentication Type': authtype,
        'Authentication Servers': authservers,
        'Accounting Servers': acctservers,
        'RadSec': radsec,
        'Edge Tunnel': mxtunnel_name,
        'WLAN Last Modified': modifiedtime    
        }
        WLAN_Array.append(values)

def format_site_report():
    #Create Data Array for Site Configuration Report
    org_site_data = get_data(Data_Array, org_sites)
    site_dict = create_id_name_dict(org_site_data)
    site_data = get_all_site_data(site_dict)
    count = count_values(site_data)
    Full_Site_Data = merge_data(org_site_data, site_data)
    sitegroupdict = create_id_name_dict(get_data(Data_Array, org_sitegroups))
    rftemplatedict = create_id_name_dict(get_data(Data_Array, rftemplates))
    alarmtemplatedict = create_id_name_dict(get_data(Data_Array, alarmtemplates))
    for site in Full_Site_Data:
        for name, data in site.items():
            sitename = name
            upgrade = data.get('auto_upgrade', {}).get('enabled')
            version = data.get('auto_upgrade', {}).get('version')
            if version == "custom":
                ap43version = data.get('auto_upgrade', {}).get('custom_versions', {}).get('AP43')
                ap33version = data.get('auto_upgrade', {}).get('custom_versions', {}).get('AP33')
            else:
                ap43version = 'NA'
                ap33version = 'NA'
            if upgrade is True or upgrade == 'true':
                    dayofweek = data.get('auto_upgrade',{}).get('day_of_week')
                    timeofday = data.get('auto_upgrade',{}).get('time_of_day')
            else:
                dayofweek = 'NA'
                timeofday = 'NA'
            if 'proxy' in data:
                proxy = data['proxy']['url']
            else:
                proxy = 'none'
            siteid = data.get('site_id')
            address = data.get('address')
            timezone = data.get('timezone')
            sitegroupsid = data.get('sitegroup_ids')
            sitegroupname = convert_ids_list(sitegroupsid, sitegroupdict)
            rftemplateid = data.get('rftemplate_id')
            rftemplatename = convert_ids_str(rftemplateid, rftemplatedict)
            sitemodifiedtime = str(datetime.fromtimestamp(data.get('modified_time')))
            alarmtemplateid = data.get('alarmtemplate_id')
            alarmtemplatename = convert_ids_str(alarmtemplateid, alarmtemplatedict)
            configpersistence = data.get('persist_config_on_device')
            #Set columns for each site
            values = {
            'Site Name': sitename,
            'Site ID': siteid,
            'Address': address,
            'Time Zone': timezone,
            'Site Groups': sitegroupname,
            'Auto Upgrade': upgrade,
            'Day Of Week': dayofweek,
            'Time of Day': timeofday,
            'AP43 Version': ap43version,
            'AP33 Version': ap33version,
            'Site Proxy': proxy,
            'Device Config Persistence': configpersistence,
            'RF Template': rftemplatename,
            'Alarm Template': alarmtemplatename,
            'Site Last Modified': sitemodifiedtime
            }
            Site_Array.append(values)


############################################################

# Compile reports and generate files

debug = 0

def main():
    try:
        start_time = time.time()
        get_all_org_data()
        format_org_report()
        format_wlan_report()
        format_site_report()
        if debug == 1:
            print (json.dumps(Org_Array, indent=2))
            print("#####################################################")
            print (json.dumps(WLAN_Array, indent=2))
            print("#####################################################")
            print (json.dumps(Site_Array, indent=2))
        if debug == 0:
            org_df = pd.DataFrame(Org_Array) 
            wlan_df = pd.DataFrame(WLAN_Array) 
            site_df = pd.DataFrame(Site_Array)                
            new_file = '{}/Mist_WiFi_Report_{}.xlsx'.format(output_location, date.today())
            with pd.ExcelWriter(new_file) as writer:
                org_df.to_excel(writer, sheet_name="Org Report")
                wlan_df.to_excel(writer, sheet_name="WLAN Report")
                site_df.to_excel(writer, sheet_name="Site Report")
            print (f"\nCreated Report:", new_file)
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)
    except KeyboardInterrupt:
        print("Cancelled By User")  

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
