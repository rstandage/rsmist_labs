#!/usr/bin/env python3

'''
This script is used to track live user session, format useful data and print to screen
'''

import json, requests
import time
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")
site_id = os.getenv("SITE_ID")

    # Create URLs
base_url = "https://api.mist.com/api/v1"
site_clients_url = '{}/sites/{}/stats/clients'.format(base_url, site_id)
map_url = '{}/sites/{}/maps'.format(base_url, site_id)

    # define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

timer = 3 # time between calls (secs)
api_count = 0
map_dict = {}


def get_mapid():
    global api_count
    global map_dict
    resp1 = requests.get(map_url, headers=headers )
    data1 = resp1.json()
    api_count = api_count+1
    for i in data1:
        mapid = (i['id'])
        mapname = (i['name'])
        map_dict[mapid] = mapname


#get data test
def get_client_details():

    global api_count
    global map_dict
    resp2 = requests.get(site_clients_url, headers=headers )
    data2 = resp2.json()
    api_count = api_count+1
    print(json.dumps(data2, indent=2))
    for client in data2:
        print ("Username: ", client['username'])
        print ("IP: ", client['ip'])
        print ("MAC: ", client['mac'])
        map_id = str(client['map_id'])
        if map_id in map_dict:
            map_name = map_dict[map_id]
        print ("Map ID: ", map_name)
        print ("Vendor: ", client['manufacture']) 
        print ("Connected: ", dt.datetime.fromtimestamp(client['assoc_time']))
        print ("Duration h/m/s:", dt.timedelta(seconds=(client['uptime'])))
        print ("SSID:", client['ssid'])
        print ("Security", client['key_mgmt'])
        print ("***************************")
        print ()



def main():
# Loop through functions
    get_mapid()
#    print (map_dict)
    try:
        while True:
            get_client_details()
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
