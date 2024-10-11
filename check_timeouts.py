#!/usr/bin/env python3

'''

This script checks session timeouts for all orgs associated to a user token

'''

import json, requests, time 
from prettytable import PrettyTable

api_token = ''
base_url = "https://api.eu.mist.com/api/v1" #change depending on endpoint
mist_api_count = 0

mist_headers = {
'Content-Type': 'application/json',
'Authorization': 'Token {}'.format(api_token)
}

############################################################ñ

def get_from_mist(url):
    global mist_api_count
    try:
        resp = requests.get(url, headers=mist_headers)
        resp.raise_for_status()  # Check for HTTP errors
        mist_api_count += 1
        data = json.loads(resp.text)
        return data
    except Exception as e:
        print(f"Error in API request: {e}")
        return None

def get_settings(id):
    # Gets org timeout
    url = '{}/orgs/{}/setting'.format(base_url, id)
    data = get_from_mist(url)
    timeout = data.get('ui_idle_timeout', 0)
    return timeout


def get_data():
    #gets all available orgs for a token
    Orgs_Array = []
    url = '{}/self'.format(base_url)
    data = get_from_mist(url)
    count = len(data['privileges'])
    print ("Getting data for {} Organisations".format(count))
    for i in data['privileges']:
        org = {
        "id" : i.get("org_id"),
        "name": i.get("name"),
        "role": i.get("role")
        }
        if i.get('scope') == 'org':
            timeout = get_settings(i.get("org_id"))
            org['timeout'] = timeout
            Orgs_Array.append(org)
    return Orgs_Array

def print_table(array):
#gets input from user
    table = PrettyTable()
    table.field_names = ["#", "Name", "ID", "ROLE", "IDLE_TIMEOUT"]
    for i, option in enumerate(array, start=1):
        table.add_row([i, option['name'], option['id'], option['role'],option['timeout']])
    print(table)

############################################################

def main():
    global mist_api_count
    Array = get_data()
    Sorted_Array = sorted(Array, key=lambda x: x['timeout'], reverse=True)
    print_table(Sorted_Array)
    print ("Mist API Count = {}".format(mist_api_count))

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or base_url == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('base_url={}'.format(base_url))
    else:  
        main() 

