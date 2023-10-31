import os
import json
import traceback
from dotenv import load_dotenv
from pymongo.collection import Collection

import requests

# local
from models import NCNews, NCSearchResp


_NEWS_SEARCH_ENDPOINT = 'https://api.newscatcherapi.com/v2/search'
CURATED_DATA_SOURCES = [
    "nytimes.com",
    "theguardian.com",
    "bloomberg.com",
    "cnbc.com",
    "wsj.com",
    "ft.com",
    "bbc.co.uk",
    "investopedia.com",
    "businessinsider.com",
    "forbes.com",
    "apnews.com",
    "reuters.com",
]
_STR_CUREATED_DATA_SOURCES = ",".join(CURATED_DATA_SOURCES)

_KEY_NC_SEARCH_ARTICLES = "articles"

# load API_KEY env
load_dotenv("./env_files/.env")
_API_KEY = os.getenv("NEWS_CATCHER_API_KEY")


def get_nc_headers():
    return { 'x-api-key': _API_KEY}


def nc_news_search(
    params,
    endpoint: str = _NEWS_SEARCH_ENDPOINT,
) -> requests.Response | None:
    try:
        response = requests.get(
            endpoint,
            headers=get_nc_headers(),
            params=params,
        )
        response.raise_for_status()
        if response.status_code == 200:
            return response
    except Exception as ex:
        traceback.print_exc()
        print(f"Error: {ex}")


def get_news_nc(
    # Ref: https://docs.newscatcherapi.com/api-docs/endpoints/search-news#advanced-query-q-parameter
    advanced_query: str = "electric vehicle",
    page_size: int = 5,
    page: int = 1,  # page * page_size = total count
    sources: str = _STR_CUREATED_DATA_SOURCES,
    lang: str = "en",
    sort_by: str = "date",
    not_sources: str | None = None,
    from_datetime: str | None = None,  # "YYYY/mm/dd HH:MM:SS" in UTC
    to_datetime: str | None = None,
    mongo_col_news: Collection | None = None,  # to save to DB each news item
) -> NCSearchResp | None:
    params = {
        'q': advanced_query,
        'lang': lang,
        'sources': sources,
        'page_size': page_size,
        'page': page,
        'sort_by': sort_by,
    }

    # optional
    if not_sources is not None:
        params.update({"not_sources": not_sources})
    if from_datetime is not None:
        params.update({"from": from_datetime})
    if to_datetime is not None:
        params.update({"to": to_datetime})

    # make the request
    resp = nc_news_search(params=params)
    if resp is None:
        print("No response valid!")
        return

    # construct model data from the response
    resp_json = resp.json()
    if resp_json['status'] != 'ok':
        print(f"NC API returned status: {resp_json['status']}")
        return None

    articles = resp_json.pop(_KEY_NC_SEARCH_ARTICLES)

    search_resp = NCSearchResp(
        status=resp_json["status"],
        total_hits=resp_json["total_hits"],
        page=resp_json["page"],
        total_pages=resp_json["total_pages"],
        page_size=resp_json["page_size"],
        user_input=json.dumps(resp_json["user_input"]),
    )

    for res in articles:
        news = NCNews(
            title=res["title"],
            author=res["author"],
            published_date=res["published_date"],
            published_date_precision=res["published_date_precision"],
            link=res["link"],
            clean_url=res["clean_url"],
            excerpt=res["excerpt"],
            summary=res["summary"],
            rights=res["rights"],
            rank=res["rank"],
            topic=res["topic"],
            country=res["country"],
            language=res["language"],
            authors=res["authors"],
            media=res["media"],
            is_opinion=res["is_opinion"],
            twitter_account=res["twitter_account"],
            match_score=res["_score"],
            api_entity_id=res["_id"],
            # parent search
            nc_search_id=str(search_resp.id),
        )
        if mongo_col_news is None:
            print(news)  # verify result
        else:
            mongo_col_news.insert_one(news.model_dump())
        search_resp.news_ids.append(str(news.id))
    
    return search_resp


if __name__ == "__main__":
    # test fetch news
    resp: NCSearchResp | None = get_news_nc()
    if resp:
        print(resp)
