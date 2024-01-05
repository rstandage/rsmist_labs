#!/usr/bin/env python3

'''
Sends a webhook with some JSON data 

'''

import json
import requests

webhook_url = "" #Add URL to receiver here
payload = {
    "topic": "Webhook_test",
    "data": "Sent from test server"
}

response = requests.post(
    webhook_url, 
    data=(json.dumps(payload, indent=2)),
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    raise ValueError(
        "Request to returned an error {}, the response is:{}".format(response.status_code, response.text)
        )
else: 
    print ("Response:", response.status_code, response.text)
