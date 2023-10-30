import json
import os
from tqdm import tqdm
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from summarization import get_summary


'''
This sample makes a call to the Bing Web Search API with a query and returns relevant web
search.
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-websearch/overview
'''

def extract_text(ith_value_response):
    '''
    This function extracts the text from the article body of a given msn url.
    '''
    url = ith_value_response["url"]
    if url.startswith("https://www.msn.com"):
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
    elif url.startswith("https://www.theguardian.com"):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', {'class': 'article-body-commercial-selector'})
        return article_body.text
    else:
        print("Article body not found")
        return "Article body not found"
def get_golden_news():
    subscription_key = '17b0e541b344457b87b0a1d1727bd8b8'

    # Query term(s) to search for.
    # Construct a request
    endpoint = 'https://api.bing.microsoft.com/v7.0/news/search'
    today = (datetime.utcnow()).strftime('%Y-%m-%d')#today's date

    params = {
        "q": "electric vehicle site:www.bloomberg.com",
        "count": 5,
        "freshness": "Day",
        "mkt": "en-US",  
    }

    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            data = []
            num_news = len(response.json()['value'])
            
            with tqdm(total=num_news, desc="Processing articles") as pbar:  # Initialize the tqdm object
                
                for i in range(num_news):
                    headline = response.json()['value'][i]['name']
                    datePublished = response.json()['value'][i]['datePublished']
                    publisher = response.json()['value'][i]['provider'][0]['name']
                    url = response.json()['value'][i]['url']
                    description = response.json()['value'][i]['description']
                    pbar.update(1)
                    tqdm.write(f"this is the {i}th article url: {url}")
                    news = {
                        "title": headline,
                        "date":datePublished,
                        "url":url,
                        "publisher":publisher,
                        "description": description,
                    }
                    data.append(news)
            return data
            # for i in range(len(response.json()['value'])):
            #     url = response.json()['value'][i]['url']
            #     text = extract_text(url)
                
            # with open(f'{today}.json', 'w') as f:
            #     json.dump(response, f)

    except Exception as ex:
        raise ex
    
def get_normal_news(event):
    subscription_key = '17b0e541b344457b87b0a1d1727bd8b8'

    # Query term(s) to search for.
    # Construct a request
    endpoint = 'https://api.bing.microsoft.com/v7.0/news/search'
    today = (datetime.utcnow()).strftime('%Y-%m-%d')#today's date

    params = {
        "q": f"{event}",
        "count": 5,
        "freshness": "Day",
        "mkt": "en-US",  
    }

    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            data = []
            with tqdm(total=len(response.json()['value']), desc="Processing articles") as pbar:  # Initialize the tqdm object
                for i in range(len(response.json()['value'])):
                    headline = response.json()['value'][i]['name']
                    datePublished = response.json()['value'][i]['datePublished']
                    publisher = response.json()['value'][i]['provider'][0]['name']
                    url = response.json()['value'][i]['url']
                    description = response.json()['value'][i]['description']
                    pbar.update(1)
                    tqdm.write(f"this is the {i}th article url: {url}")
                    news = {
                        "title": headline,
                        "date":datePublished,
                        "url":url,
                        "publisher":publisher,
                        "description": description,
                    }
                    data.append(news)
            return data
            # for i in range(len(response.json()['value'])):
            #     url = response.json()['value'][i]['url']
            #     text = extract_text(url)
                
            # with open(f'{today}.json', 'w') as f:
            #     json.dump(response, f)

    except Exception as ex:
        raise ex
