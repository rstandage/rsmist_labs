#!/usr/bin/env python3

'''
Sends a webhook with some JSON data to slack

'''

import json
import requests


#Variables
base_url = "hooks.slack.com/services"
path = ""

#Values
webhook_url = "https://{}/{}".format(base_url, path)
title = (f"New Incoming Message :zap:")
payload = {
    "topic": "device-events",
    "events": [
        {
            "audit_id": "a8ec4d8a-4da6-4ead-a486-d0f72e40dd08",
            "ap": "5c5b35000001",
            "ap_name": "AP41 Near Lab",
            "device_name": "AP41 Near Lab",
            "device_type": "ap/switch/gateway",
            "ev_type": "NOTICE",
            "mac": "5c5b35000001",
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "reason": "power_cycle",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "site_name": "Site 1",
            "text": "event details",
            "timestamp": 1647470730,
            "type": "AP_RESTARTED"
        }
    ]
}

slack_data = {
    "username": "WebhookFromDev",
    "icon_emoji": ":alarm:",
    #"channel" : "#somerandomcahnnel",
    "attachments": [
        {
            "color": "#9733EE",
            "fields": [
                {
                    "title": title,
                    "value": json.dumps(payload, indent=2),
                    "short": "false",
                }
            ]
        }
    ]
}
response = requests.post(
    webhook_url, 
    data=json.dumps(slack_data),
    params=(json.dumps(payload, indent=2)),
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    raise ValueError(
        "Request to returned an error {}, the response is:{}".format(response.status_code, response.text)
        )
else: 
    print ("Response:", response.status_code, response.text)
