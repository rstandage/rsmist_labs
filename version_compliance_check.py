#!/usr/bin/env python3

'''
THis script checks software version of a particular hardwqre type and validates it against the site config

'''

import json, requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")
site_id = os.getenv("SITE_ID")

hw_type = "AP41"

    # Create URLs
base_url = "https://api.mist.com/api/v1"
site_config_url = '{}/sites/{}/setting'.format(base_url, site_id)
device_stats_url = '{}/sites/{}/stats/devices'.format(base_url, site_id)
version_options_url = '{}/sites/{}/devices/versions'.format(base_url, site_id)

print (device_stats_url)

    # define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

timer = 5 # time between calls (secs)
api_count = 0
site_policy = ""
site_version = ""

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

############################################################

def check_site_version():
#Get version set on site settings

    global api_count
    global site_policy
    resp1 = requests.get(site_config_url, headers=headers )
    data1 = json.loads(resp1.text)
    site_policy = (data1['auto_upgrade']['version'])
    api_count = api_count+1
    

def check_all_versions():
#check available version to find rev number of policy

    global api_count
    global site_policy
    global site_version
    hw = hw_type
    resp2 = requests.get(version_options_url, headers=headers )
    data2 = json.loads(resp2.text)
    api_count = api_count+1
    #If version shares the same tag as the site policy, return the version number
    for ver in data2:
        if ((ver['tag']) == site_policy) and ((ver['model']) == hw):
            site_version = (ver['version'])


def check_devices():
#Checks for compliance and prints specified data for APs

    global api_count
    global site_version

    resp3 = requests.get(device_stats_url, headers=headers )
    data3 = json.loads(resp3.text)
    api_count = api_count+1
    if resp3.status_code!=200:
        print ("")
        print (resp3.text)
        print ("Total API Calls Used For This Report ",api_count)
    for device in data3:
        print(f"\tDEVICE NAME: {device['name']}")
        print(f"\tIP: {device['ip']}")
        print(f"\tMAC: {device['mac']}")    
        print(f"\tVERSION: {device['version']}")
        #Check for compliance against site settings. 
        if (device['version']) == site_version:
            print (f"\t{bcolors.OKGREEN}***COMPLIANT***{bcolors.ENDC}")
        else:
            print (f"\t{bcolors.FAIL}***NON-COMPLIANT***{bcolors.ENDC}")
            #Exit if no values for upgrades as this takes a few mins to come in 
            try: 
                print(f"\tScheduled Version: {device['auto_upgrade_stat']['scheduled_version']}")
                print(f"\tScheduled Version: {device['auto_upgrade_stat']['scheduled_time']}")
            except KeyError: pass
        print()

def main():
# Loop through functions
    print(f"{bcolors.HEADER}** Polling For Device Compliance...\n{bcolors.ENDC}")
    try:
        while True:
            check_site_version()
            check_all_versions()
            print (f"{bcolors.BOLD}Site Policy is set to: {bcolors.ENDC}", site_policy, site_version )
            check_devices()
            time.sleep(timer)            
    except KeyboardInterrupt:
        pass 

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or site_id == '' or org_id == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('site_id={}'.format(site_id))
        print('org_id={}'.format(org_id))
    else:    
        start_time = time.time()
        #Run
        main()
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)
