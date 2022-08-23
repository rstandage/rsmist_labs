#!/usr/bin/env python3

"""
Gets logs periodically based on timer variable and prints JSON to screen

"""

import json, requests, time
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

    # Create URLs
base_url = "https://api.mist.com/api/v1"
org_log_url = '{}/orgs/{}/logs?'.format(base_url, org_id)

    # define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }


timer = 60 # time between calls (secs)
api_count = 0

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

###########################################################

def fetch_logs():
    global api_count
    start = time.time() - timer
    end = time.time()
    url1 = '{}start={}&end={}'.format(org_log_url, start, end)
    print ()
    resp1 = requests.get(url1, headers=headers )
    data1 = json.loads(resp1.text)
    api_count = api_count+1
    print (f"{bcolors.HEADER}Collecting Logs{bcolors.ENDC} From:", dt.datetime.fromtimestamp(start), "To:", dt.datetime.fromtimestamp(end))
    if data1['total'] > 0:
        print (json.dumps(data1, indent=2))
    else:
        print (f"{bcolors.OKGREEN}Nothing To Report{bcolors.ENDC}\n\n")
            
              
def main():
# Loop through functions
    print(f"{bcolors.BOLD}** Polling For Logs...\n{bcolors.ENDC}")
    try:
        while True:
            fetch_logs()
            time.sleep(timer)            
    except KeyboardInterrupt:
        pass 

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
    else:    
        start_time = time.time()
        #Run
        main()
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)
