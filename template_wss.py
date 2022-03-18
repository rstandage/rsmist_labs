#!/usr/bin/env python3

'''
Basic WSS request to Mist test channel. Prints events

'''

import json, websocket

#Define Variables
api_token = ""
org_id = ""
site_id = ""

# Create URLs
base_url = "wss://api-ws.mist.com/api-ws/v1/stream"
test_sub = '/test'
logging_sub = '/sites/{}/alarms/search'.format(site_id)

# define standard headers
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

#Modify this value with the required sub
sub=logging_sub

def on_message(ws, message):
    global msg_received
    print ('onmessage', message)
    msg_received += 1
    if msg_received > 3:
        ws.send(json.dumps({'unsubscribe': sub}))
        ws.close()


def on_error(ws, error):
    print ('onerror')


def on_close(ws):
    print ('onclose')


def on_open(ws):
    print ('onopen')
    ws.send(json.dumps({'subscribe': sub}))


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        base_url,
        header=headers,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()
