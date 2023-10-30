import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


'''
This sample makes a call to the Bing Web Search API with a query and returns relevant web
search.
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-websearch/overview
'''

def extract_text(url):
    '''
    This function extracts the text from the article body of a given msn url.
    '''
    last_dash_index = url.rfind('-')
    substring = url[last_dash_index + 1:]
    targetstring = 'https://assets.msn.com/content/view/v2/Detail/en-us/'+substring
    response = requests.get(targetstring)
    response.raise_for_status()  # Check if the request was successful
    data = response.json()
    body = data.get("body", "Body not found")
    soup = BeautifulSoup(body, 'html.parser')
    
    # Find the paragraph with text 'Most Read from Bloomberg'
    most_read_tag = soup.find('p', text='Most Read from Bloomberg')
    # If found, extract the tag and the following two tags (ul and p)
    if most_read_tag:
        most_read_tag.extract()
        most_read_tag.find_next('ul').extract()
        most_read_tag.find_next('p').extract()
        
    for a in soup.findAll('a'):  # remove all <a> tags
        a.replace_with_children()
    text = soup.get_text(separator=' ', strip=True)
    
    return text
# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = '17b0e541b344457b87b0a1d1727bd8b8'
# Query term(s) to search for.
# Construct a request
endpoint = 'https://api.bing.microsoft.com/v7.0/news/search'
today = (datetime.utcnow()).strftime('%Y-%m-%d')#today's date
params = {
    "q": "electric vehicle",
    "count": 1,
    "freshness": "Day",
    "mkt": "en-US",  
}
headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
# Call the API
try:
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code == 200:
        with open(f'{today}.json', 'w') as f:
            json.dump(response.json()['value'], f)
        # for i in range(len(response.json()['value'])):
        #     url = response.json()['value'][i]['url']
        #     text = extract_text(url)
            
        # with open(f'{today}.json', 'w') as f:
        #     json.dump(response, f)
except Exception as ex:
    raise ex