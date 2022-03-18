#!/usr/bin/env python3

'''
Uses flask to create a webhook listener

'''

# We need to import request to access the details of the POST request
from flask import Flask, request, Response
import json, requests, time
import datetime as dt

host = "127.0.0.1" # Interface to run listener
port = 10000 # Integer for port number

# Initialize the Flask application
app = Flask(__name__)

class bcolors:
    HEADER = '\033[95m'
    ENDC = '\033[0m'

@app.route('/webhook', methods=['POST'])

def respond():
# create webhook receiver
    print (f"{bcolors.HEADER}#################  Incoming  #######################{bcolors.ENDC}")
    if request.headers['Content-Type'] != 'application/json':
        return Response(status=400, message="Expected Content-Type = application/json")
    try:
        #Get data and format payload for POST
        payload = []
        data = request.json
        print("Topic: ", data['topic'])
        for e in data['events']:
            time = dt.datetime.fromtimestamp(e['timestamp'])
            f = {
            "Event": e['type'],
            "Name": e['ap_name'],
            "Mac": e['mac'],
            "Time": str(time),
            "Reason": e['reason'] 
            }
            payload.append(f)

        print (json.dumps(payload, indent=2))
        return Response(status=200)
        return payload
        
    except Exception as e:
        print ("Error Processing request: {}".format(e))

if __name__ == '__main__':
    app.run(
        host=host,
        port=port
    )
