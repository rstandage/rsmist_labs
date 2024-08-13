#!/usr/bin/env python3

'''

This script gets current sites from a site group and backs up the AP config including images

'''

import json, requests, os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN") #change ito a string if needed
org_id = os.getenv("ORG_ID") #change ito a string if needed
# Create URLs
base_url = os.getenv("BASE_URL") #change into a string if needed
filepath = ''


# define standard headers
mist_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

mist_api_count = 0

############################################################

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

def download_file(url, dest):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

############################################################

def main():
    global mist_api_count
    sitelist = [] #Enter a list of site IDs
    for s in sitelist:
        site_info_url = '{}/sites/{}'.format(base_url, s)
        site_info = get_from_mist(site_info_url)
        if site_info is not None:
            sitename = site_info.get('name')
            print('Creating Folder for {}'.format(sitename))
            foldername = os.path.join(filepath, sitename)
            os.mkdir(foldername)
            ap_settings_url = '{}/sites/{}/devices?type=ap'.format(base_url, s)
            site_ap_details = get_from_mist(ap_settings_url)
            jsonfilename = 'ap_info.json'
            configfilename = os.path.join(filepath, sitename, jsonfilename)
            print("Backing up config for {} APs".format(len(site_ap_details)))
            with open(configfilename, 'w') as file:
                json.dump(site_ap_details, file, indent=4)
            for a in site_ap_details:
                if 'image1_url' in a:
                    name = a.get('name')
                    durl1 = a.get('image1_url')
                    image1 = '{}-image1.jpeg'.format(name)
                    imagepath = os.path.join(foldername, image1)
                    download_file(durl1, imagepath)
                if 'image2_url' in a:
                    durl2 = a.get('image2_url')
                    image2 = '{}-image2.jpeg'.format(name)
                    imagepath = os.path.join(foldername, image2)
                    download_file(durl2, imagepath)
            print("done")
        else:
            print(f"skipping {s}")
    print(f'Mist API count = {mist_api_count}')

if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or org_id == ''  or base_url == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('org_id={}'.format(org_id))
        print('base_url={}'.format(base_url))
    else:
        main()

