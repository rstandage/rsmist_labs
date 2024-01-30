#!/usr/bin/env python3

'''

This script send a ping to trigger a specific webhook for testing

'''

import json, requests, time, os
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")

# Create URLs
base_url = os.getenv("BASE_URL")
org_hooks_url = '{}/orgs/{}/webhooks'.format(base_url, org_id)

# define standard headers
mist_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

mist_api_count = 0

############################################################

def POST_to_mist(x, y):
#Sends data to mist where x is the url and y is the payload as a dict or array
    global mist_api_count
    payload = json.dumps(y)
    send = requests.request("POST", x, data=payload, headers=mist_headers)
    mist_api_count = mist_api_count+1
    text = json.loads(send.text)
    if send.status_code == 200:
        response = True
    else:
        print("Failed - HTTP Error {}".format(send.status_code))
        response = False
    return response, text

def getorghooks():
#Creates Array of pre-existing site groups
    global mist_api_count
    Hooks_Array = []
    resp0 = requests.get(org_hooks_url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data0 = json.loads(resp0.text)
    for i in data0:
        hook = {
        "id" : i.get("id"),
        "name": i.get("name"),
        "url": i.get("url")
        }
        Hooks_Array.append(hook)
    return Hooks_Array

def userselect(array):
#gets input from user
    table = PrettyTable()
    table.field_names = ["#", "Name", "ID", "URL"]
    for i, option in enumerate(array, start=1):
        table.add_row([i, option['name'], option['id'], option['url']])
    print("Please select the webhook you would like to test:")
    print()
    print(table)
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(array):
                return array[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")  

############################################################

def main():
    global mist_api_count
    HooksArray = getorghooks()
    if len(HooksArray) > 0:
        userselection = userselect(HooksArray)
        hook_id = userselection.get("id")
        ping_hook_url = '{}/orgs/{}/webhooks/{}/ping'.format(base_url, org_id, hook_id)
        data = {}
        resp, text = POST_to_mist(ping_hook_url, data)
        if resp is True:
            print ("Webhook sucessfully triggered")
    else:
        print("No org level webhooks found") 

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == '' or base_url == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
        print('base_url={}'.format(base_url))
    else:  
        main() 
