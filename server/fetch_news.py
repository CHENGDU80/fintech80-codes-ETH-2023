import os
import json
import traceback
from dotenv import load_dotenv

import requests
from datetime import datetime

# local
from models import BingNews, BingSearchResp



BING_ENDPOINT_NEWS_SEARCH = 'https://api.bing.microsoft.com/v7.0/news/search'

# load bing env
load_dotenv("./env_files/.env")
BING_API_KEY = os.getenv("BING_API_KEY")


### Special keyfields in Bing Search Response
_KEY_BING_SEARCH_VALUE = "value"


def get_bing_headers():
    return { 'Ocp-Apim-Subscription-Key': BING_API_KEY}


def get_bing_params(
    advanced_query: str,
    count: int = 1,
    freshness: str = "Week",  # or a date range
    market: str = "en-US",
    category: str | None = "Business",  # [Business, ScienceAndTechnology, Politics] for en-US
):
    """Keywords on https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/query-parameters#news-categories-by-market"""
    params = {
        "q": advanced_query,
        "count": count,
        "freshness": freshness,
        "mkt": market,
    }
    if category is not None:
        params.update({"category": category})
    return params


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
    except Exception as ex:
        traceback.print_exc()
        print(f"Error: {ex}")


def get_news(
    advanced_query: str = "electric vehicle site:www.bloomberg.com",
) -> BingSearchResp | None:
    params = get_bing_params(
        advanced_query=advanced_query,
        count=5,
        category=None,
    )
    resp = bing_news_search(params=params)
    if resp is None:
        print("No response valid!")
        return

    resp_json = resp.json()
    values = resp_json.pop(_KEY_BING_SEARCH_VALUE)
    bing_search_resp = BingSearchResp(
        query_params=json.dumps(params),
        metadata=json.dumps(resp_json),
    )

    for res in values:
        news = BingNews(
            name=res["name"],
            url=res["url"],
            image=json.dumps(res["image"]),
            description=res["description"],
            about=json.dumps(res["about"]),
            provider=json.dumps(res["provider"]),
            date_published=res["datePublished"],
            search=str(bing_search_resp.id),
        )
        bing_search_resp.news_ids.append(str(news.id))
    
    return resp


def _save_bing_results(response: requests.Response, query_params: dict):
    if response is None:
        print("NoOp! Input is None")

    file_ts = datetime.now().isoformat()
    with open(f'{file_ts}.json', 'w') as f:
        json.dump(response.json(), f)
    print(f"Response saved to {file_ts}.json")

    with open(f'{file_ts}_params.json', 'w') as f:
        json.dump(query_params, f)
    print(f"Query params saved to {file_ts}.json")


def _local_test():
    params = get_bing_params(
        advanced_query="electric vehicle site:www.bloomberg.com",
        count=5,
    )

    resp = bing_news_search(params=params)
    _save_bing_results(response=resp, query_params=params)