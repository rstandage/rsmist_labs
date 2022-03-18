#!/usr/bin/env python3

"""
Tracks a user's XY co-ordinates via a websocket
Need to add map ID and asset
THis URL is for SDK clients as its better for accuracy on the demo lab. CAn be changes to BLE/WiFi

"""

import json, websocket
import time
from datetime import datetime, timedelta

#Define Variables
api_token = ""
org_id = ""
site_id = ""

#Follow Curious George in the Live Demo
map_id = ""
AssetTagName = ""

# Create URLs
base_url = "wss://api-ws.mist.com/api-ws/v1/stream"
asset_location_sub = '/sites/{}/stats/maps/{}/sdkclients'.format(site_id, map_id)

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

#define subscription
sub = asset_location_sub

TimeDelta = datetime.now()

debug = 0 
 
def print_asset_details(message):
    #Format the message printed out
    print(f"* Received message for asset: {message['data']['name']}")
    fulltime = time.gmtime(message['data']['_time'])
    dt = datetime.fromtimestamp(message['data']['_time'])
    hours = time.strftime("%H:%M:%S", fulltime)
 
    global TimeDelta
    NewTimeDelta = dt - TimeDelta
    TimeDelta = dt
 
    print(f"\tTIME: {hours}")
    print(f"\tDELTA: {NewTimeDelta.total_seconds()} sec")
    print(f"\tX: {message['data']['x']}")
    print(f"\tY: {message['data']['y']}")
    #print(json.dumps(message, indent=4, sort_keys=True))
    print()
 
 
def on_message(ws, message):
    #Action when messages received
    message = json.loads(message)
    if 'data' not in message:
        print(json.dumps(message, indent=4, sort_keys=True))
    else:
        message['data'] = json.loads(message['data'])
        if (AssetTagName != "") and (message['data']['name'].find(AssetTagName) != -1):
            print_asset_details(message)
        elif AssetTagName == "":
            print_asset_details(message)


def on_error(ws, error):
    # Print the error
    print('Error: {}\n'.format(error))


def on_close(ws):
    # Automatically called at the end of run_forever() method
    print('Closed WebSocket connection') 
 
 
def on_open(ws):
    """Use to subscribe to a specific endpoint."""
    print('Opening WebSocket connection ...\n')
    print('Subscribing to channel:')
    print(json.dumps({'subscribe': sub}, indent=4, sort_keys=True))
    ws.send(json.dumps({'subscribe': sub}))
 
 
def establish_ws():
    if debug == 1:
        websocket.enableTrace(True) 
    ws = websocket.WebSocketApp(
        base_url,
        header=headers,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.on_open = on_open
    ws.run_forever()
 
 
if __name__ == '__main__':
    # Ensure variables are defined
    if api_token == '' or site_id == '' or sub == '':
        print('Check for Missing variables:')
        print('api_token={}'.format(api_token))
        print('site_id={}'.format(site_id))
        print('sub={}'.format(sub))
    else:    
        start_time = time.time()
        print('** GETTING LOCATION DATA FOR ASSET TAGS...\n')
        #Run 
        establish_ws()
        run_time = time.time() - start_time
        print(f"\n** Time to run: {round(run_time, 2)} sec")