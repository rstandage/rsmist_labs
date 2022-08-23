#!/usr/bin/env python3

"""
Gets logs based on user input and creates csv
"""

import json, requests, time
from datetime import datetime, date
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv("")

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")


    # Create URLs
base_url = os.getenv("BASE_URL")
org_log_url = '{}/orgs/{}/logs?'.format(base_url, org_id)
org_site_list = '{}/orgs/{}/sites'.format(base_url, org_id)

    # define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

api_count = 0
newfile_location = "./"

###########################################################

def get_timer():
    #Gets timer counter in seconds
    timer = 86400
    userinput = input("Get logs for last [x] Seconds (Default 86400): ")
    if userinput != "":
        timer = int(userinput)
    return timer

def convert_ids_str(x, y):
    #Converts IDs into names based on dict (x)
    namestr = ""
    for i, n in y.items():
        if x == i:
            namestr = n
    return namestr

def get_sitesdict():
    global api_count
    sites_dict = {}
    #Get Org site data
    resp1 = requests.get(
        org_site_list, 
        headers=headers)
    api_count = api_count+1
    data1 = json.loads(resp1.text)
    for i in data1:
        sites_dict[i['id']] = i['name']
    return sites_dict

def fetch_logs(x):
    #Grab Logs from Mist
    global api_count
    start = time.time() - x
    end = time.time()
    url1 = '{}start={}&end={}&limit=1000'.format(org_log_url, start, end)
    print ()
    resp1 = requests.get(url1, headers=headers )
    data1 = json.loads(resp1.text)
    api_count = api_count+1
    print ("Collecting Logs From:", 
        datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S"), 
        "To:", datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S"))
    return data1
    try:
        if data1['total'] > 0:
            return data1
        else:
            print ("Nothing To Report")
            pass
    except KeyError:
        pass

def create_Array(x, y):
    #Creates Array
    Site_Array = []
    for r in x['results']:
        sitename = convert_ids_str(r.get("site_id"), y)
        values = {
        'Time': str(datetime.fromtimestamp(r.get("timestamp"))),
        'User': r.get("admin_name"),
        'Source IP': r.get("src_ip"),
        "Message": r.get("message"),
        "Site Name": sitename,
        "Before": r.get("before"),
        "After": r.get("after")
        }
        Site_Array.append(values)
    return Site_Array


###########################################################

def main():
    try:
        secs = get_timer()
        print("Polling For Logs")
        data = fetch_logs(secs)
        sitesdict = get_sitesdict()
        Site_Array = create_Array(data, sitesdict)
        df = pd.DataFrame(Site_Array)
        new_file = '{}audit_report_{}.csv'.format(newfile_location, date.today())
        print (f"\nCreated Report:", new_file)
        df.to_csv(new_file)           
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
