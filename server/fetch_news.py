import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import traceback


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


def get_bing_headers():
    return { 'Ocp-Apim-Subscription-Key': '17b0e541b344457b87b0a1d1727bd8b8'}


def get_bing_params(
    advanced_query: str,
    count: int = 1,
    freshness: str = "Week",  # or a date range
    market: str = "en-US",
    category: str = "Business",  # [Business, ScienceAndTechnology, Politics] for en-US
):
    """Keywords on https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/query-parameters#news-categories-by-market"""
    return {
        "q": advanced_query,
        "count": count,
        "freshness": freshness,
        "mkt": market,
        "category": category,
    }


BING_ENDPOINT_NEWS_SEARCH = 'https://api.bing.microsoft.com/v7.0/news/search'


def bing_news_search(
    params,
    endpoint: str = BING_ENDPOINT_NEWS_SEARCH,
) -> requests.Response | None:
    try:
        response: requests.Response = requests.get(
            endpoint,
            headers=get_bing_headers(),
            params=params,
        )
        response.raise_for_status()
        if response.status_code == 200:
            return response
            # for i in range(len(response.json()['value'])):
            #     url = response.json()['value'][i]['url']
            #     text = extract_text(url)
                
            # with open(f'{today}.json', 'w') as f:
            #     json.dump(response, f)
    except Exception as ex:
        traceback.print_exc()
        print("Error: ex")


def save_bing_results(response: requests.Response, query_params: dict):
    if response is None:
        print("NoOp! Input is None")

    file_ts = datetime.now().isoformat()
    with open(f'{file_ts}.json', 'w') as f:
        json.dump(response.json(), f)
    print(f"Response saved to {file_ts}.json")

    with open(f'{file_ts}_params.json', 'w') as f:
        json.dump(query_params, f)
    print(f"Query params saved to {file_ts}.json")


def _main():
    params = get_bing_params(
        advanced_query="electric vehicle site:www.bloomberg.com",
        # (
        #     '"electric vehicle" OR "BYD" OR "Tesla" '
        #     'EV Market, Policy & Investment'
        #     'EV Battery Summit '
        #     'Sustainable EV Supply Chain '
        #     'EV Manufacturing '
        #     'Next Generation Vehicle Design '
        #     'Advanced Driver Assistance System '
        #     'EV Charging Infra '
        #     "site:www.bloomberg.com"
        #     # " AND "
        #     # "intitle:electric%20vehicle OR inbody:electric%20vehicle )",
        # ),
        count=5,
    )

    resp = bing_news_search(params=params)
    save_bing_results(response=resp, query_params=params)


if __name__ == "__main__":
    _main()
