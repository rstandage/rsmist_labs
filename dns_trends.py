import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json, requests, os

api_token = ''
limit = 1000 #Modify the amount of items that are pulled back at a time

# Create URLs
base_url = 'https://api.eu.mist.com/'
site_id = ''
event_name = 'MARVIS_DNS_FAILURE'
ws_ce_url = '{}api/v1/sites/{}/clients/events/search?type={}&limit={}&duration=1d'.format(
    base_url, site_id, event_name, limit )

# define standard headers
mist_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token {}'.format(api_token)
        }

mist_api_count = 0
count = 0
Data_Array = []

############################################################

def get_inital_results(url):
#function to get the initial data and add to the array. also returns total and the 'next'
    global mist_api_count
    global count
    global Data_Array
    resp = requests.get(url, headers=mist_headers)
    mist_api_count = mist_api_count+1
    data = json.loads(resp.text)
    for i in data.get('results'):
        Data_Array.append(i)
    count += len(data.get('results'))
    total = data.get('total')
    nexturl = data.get('next')
    return total, nexturl


def get_next_results(nexturl):
#function to get the data and add to the array. also returns the 'next'
    global mist_api_count
    global count
    global Data_Array
    try:
        url = base_url+nexturl
        resp = requests.get(url, headers=mist_headers)
        mist_api_count = mist_api_count+1
        data = json.loads(resp.text)
        for i in data.get('results'):
            Data_Array.append(i)
        count += len(data.get('results'))
        nexturl = data.get('next')
        return nexturl
    except Exception as e:
        print("An error occurred: {}".format(e))
        print("failed at count {}".format(count))
        print("next url was: {}".format(url))
        return None

total, nexturl = get_inital_results(ws_ce_url)
print ("Getting Data for {} Items".format(total))
while count is not total:
    if nexturl is not None:
        nexturl = get_next_results(nexturl)
    else:
        print("Completed Data Collection")
        break


# Read the CSV file
df = pd.DataFrame(Data_Array)

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

# Group by time (minute) and SSID
dns_failures = df.groupby([pd.Grouper(key='datetime', freq='1min'), 'ssid']).size().reset_index(name='count')

# Create the plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=dns_failures, x='datetime', y='count', hue='ssid', marker='o')

# Customize the plot
plt.title('DNS Failures Trend by WLAN (SSID)', pad=20)
plt.xlabel('Time')
plt.ylabel('Number of DNS Failures')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='SSID', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()

# Print summary statistics
print("\nSummary of DNS Failures by SSID:")
summary = df.groupby('ssid').size().reset_index(name='Total Failures')
print(summary)
