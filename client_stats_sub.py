#!/usr/bin/env python3

import json, websocket, 
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
org_id = os.getenv("ORG_ID")
site_id = os.getenv("SITE_ID")

# Create URLs
base_url = "wss://api-ws.mist.com/api-ws/v1/stream"
test_sub = '/test'
client_sub = '/sites/{}/stats/clients'.format(site_id)

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

#Modify this value with the required sub
sub=client_sub

# connection will close once threshold is met, 0 for infinite
max_msg_received = 50
msg_received = 0

debug = 0

# Receive the WebSocket events, and unubscribe from the endpoint
def on_message(ws, message):
    global msg_received

    msg_received += 1

    print('Received message {}: '.format(msg_received))

    message = json.loads(message)
    if 'data' not in message:
        print(json.dumps(message, indent=4, sort_keys=True))
    else:
        message['data'] = json.loads(message['data'])
        print(json.dumps(message, indent=4, sort_keys=True))
    print()

    if msg_received == max_msg_received:
        print('Unsubscribing from channel:')
        print(json.dumps({'unsubscribe': sub}, indent=4, sort_keys=True))
        ws.send(json.dumps({'unsubscribe': sub}))
        print()
        ws.close()

# Print the error
def on_error(ws, error):
    print('Error: {}\n'.format(error))

# Automatically called at the end of run_forever() method
def on_close(ws):
    print('Closed WebSocket connection') 

# Subscribe to the endpoint on open
def on_open(ws):
    print('Opening WebSocket connection ...\n')
    print('Subscribing to channel:')
    print(json.dumps({'subscribe': sub}, indent=4, sort_keys=True))
    ws.send(json.dumps({'subscribe': sub}))
    print()

# Establish WebSocket connection
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
        print('Missing variables:')
        print('api_token={}'.format(api_token))
        print('site_id={}'.format(site_id))
        print('sub={}'.format(sub))

    # Establish WebSocket
    establish_ws()
