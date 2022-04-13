#!/usr/bin/env python3

'''
This script checks every sites configuration and creates a report

'''
import json, requests
import pandas
import time
import os
from dotenv import load_dotenv
from datetime import date
from copy import deepcopy

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

# Create URLs
base_url = "https://api.mist.com/api/v1"
org_site_list = '{}/orgs/{}/sites'.format(base_url, org_id)


#Set location for reports to be stored
output_location = ''

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

api_count = 0
sites_dict = {}
Site_Array = []

############################################################

def get_site_dict():
#Get list of sites
    global api_count
    global sites_dict
    resp0 = requests.get(
        org_site_list, 
        headers=headers)
    api_count = api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        sites_dict[i['name']] = i['id']

def get_site_config(x):
#Get version set on site settings

    global api_count
    global Site_Array
    for site_name, site_id in x.items():
        site_config_url = '{}/sites/{}/setting'.format(base_url, site_id)
        resp1 = requests.get(
            site_config_url, 
            headers=headers )
        api_count = api_count+1
        data1 = json.loads(resp1.text)
        site_data = {'site name': site_name}
        site_data.update(data1)
        Site_Array.append(site_data)
        print(".")


def cross_join(left, right):
    new_rows = [] if right else left
    for left_row in left:
        for right_row in right:
            temp_row = deepcopy(left_row)
            for key, value in right_row.items():
                temp_row[key] = value
            new_rows.append(deepcopy(temp_row))
    return new_rows


def flatten_list(data):
    for elem in data:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem


def json_to_dataframe(data_in):
    def flatten_json(data, prev_heading=''):
        if isinstance(data, dict):
            rows = [{}]
            for key, value in data.items():
                rows = cross_join(rows, flatten_json(value, prev_heading + '.' + key))
        elif isinstance(data, list):
            rows = []
            for item in data:
                [rows.append(elem) for elem in flatten_list(flatten_json(item, prev_heading))]
        else:
            rows = [{prev_heading[1:]: data}]
        return rows

    return pandas.DataFrame(flatten_json(data_in))


def main():
        start_time = time.time()
        print(f"** Polling For Site Details...**")
        get_site_dict()
        get_site_config(sites_dict)
        df = json_to_dataframe(Site_Array)        
        new_file = '{}/site_template_report_{}.csv'.format(output_location, date.today())
        print (f"\nCreated Report:", new_file)
        df.to_csv(new_file)
        run_time = time.time() - start_time
        print(f"\nTime to run: {round(run_time, 2)} sec")
        print(f"\nAPI count: ", api_count)  

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
    else:  
        main()  



