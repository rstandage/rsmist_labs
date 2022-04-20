#!/usr/bin/env python3

"""
Originally Written by Rory Standage - Juniper Networks

This script gets logs from ORG based on time period between now and now minus the value set in timer

HEC needs to be set up on Splunk https://docs.splunk.com/Documentation/Splunk/8.2.5/Data/UsetheHTTPEventCollector

This is a demonstration of the functionality and not intended for production

Use case is where inbound websockets are not allowed from the cloud

"""

import json, requests, time
import datetime as dt
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

##turns off the warning that is generated below because Splunk is using a self signed ssl cert
urllib3.disable_warnings()

########### Define Variables ###############################

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

splunk_token = os.getenv("SPLUNK_TOKEN") #Insert HEC Token

# Create URLs
base_url = "https://api.mist.com/api/v1"
org_log_url = '{}/orgs/{}/logs?'.format(base_url, org_id)
splunk_host = "splunk.netservice.home" #Host Address for Splunk Server
splunk_HEC_port = 8088 #Listening port for HEC
splunk_url='https://{}:{}/services/collector/event'.format(splunk_host, splunk_HEC_port)

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

splunk_header= {
        'Content-Type': 'application/json',
        'Authorization': 'Splunk {}'.format(splunk_token)
        }

###### Add Proxy information ########
use_proxy = "no"

proxies = {
   'http': 'http://proxy.example.com:8080',
   'https': 'http://secureproxy.example.com:8090'
}

timer = 3600 * 4 # time between calls (secs)
api_count = 0

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

###########################################################

def send_to_splunk(message):
#Bundle message and forward to Splunk    
    payload = {
        "event" : message,
        }
    response = requests.post(
        splunk_url, 
        headers=splunk_header, 
        data=json.dumps(payload),
        verify=False
        )

    if response.status_code != 200:
        raise ValueError(
            "Request to Splunk returned an error {}, the response is:{}".format(response.status_code, response.text)
            )
    else: 
        print (f"\t{bcolors.YELLOW}Data Sent To Splunk HEC{bcolors.ENDC}", response.status_code, response.text, "\n")  

def fetch_logs():
    global api_count
    start = time.time() - timer
    end = time.time()
    url1 = '{}start={}&end={}'.format(org_log_url, start, end)
    try:
        if use_proxy == "yes":
            resp1 = requests.get(url1,
                headers=headers,
                proxies=proxies )
        else:
            resp1 = requests.get(url1,
                headers=headers)            
        response = resp1  
        data1 = json.loads(resp1.text)
        api_count = api_count+1
        print (f"{bcolors.HEADER}Collecting Logs{bcolors.ENDC} From:", dt.datetime.fromtimestamp(start), "To:", dt.datetime.fromtimestamp(end))
        if data1['total'] > 0:
            data2 = data1['results']
            print("\t{} New Records Found".format(data1['total']))
            send_to_splunk(data2)
        else:
            print (f"{bcolors.OKGREEN}Nothing To Report{bcolors.ENDC}\n")

    except requests.exceptions.RequestException as e:
        raise SystemExit(e) 

              
def main():
# Loop through functions
    hours = str(round(((timer/60)/60), 2))
    print(f"{bcolors.BOLD}** Polling For Logs Every " +hours+ " Hours **\n")
    try:
        while True:
            fetch_logs()
            time.sleep(timer)            
    except KeyboardInterrupt:
        pass 

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == '' or splunk_token =='' or splunk_host == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
        print('splunk_token={}'.format(splunk_token))
        print('splunk_host={}'.format(splunk_host))
    else:    
        start_time = time.time()
        #Run
        main()
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)
