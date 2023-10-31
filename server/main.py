from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

# local import
from llm_completion import (
    llm_complete_chat,
    llm_construct_chat_keyword_gen,
)

from models import (
    BingNews,
    BingSearchResp,
    Event,
    Company,
    NCNews,
    NCSearchResp,
)
from db_connections import db_conn_mongo, db_conn_redis
from fetch_news_bing import get_news_bing
from fetch_news_catcher import get_news_nc, CURATED_DATA_SOURCES


### DB conn ####################################################################
# Mongo
col_company = db_conn_mongo.get_collection(database_name="main", collection_name="company")
col_event = db_conn_mongo.get_collection(database_name="main", collection_name="event")
# bing API news
col_bingnews = db_conn_mongo.get_collection(database_name="main", collection_name="bingnews")
col_bingsearchresp = db_conn_mongo.get_collection(database_name="main", collection_name="bingsearchresp")
# news catcher API news
col_nc_news = db_conn_mongo.get_collection(database_name="main", collection_name="ncnews")
col_nc_search_resp = db_conn_mongo.get_collection(database_name="main", collection_name="ncsearchresp")
# redis
rdb = db_conn_redis.get_rdb()


### Simple token for get requests
SIMPLE_TOKEN = "K6tyfzrSrVjRHHqOaeHNI3OM7IPk82ky"


### APP setup ##################################################################


app = FastAPI()

origins = [
    "http://localhost:8080"  # Replace with the frontend server 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def test_conn():
    return {"ping": "pong"}

@app.get("/getfakedata")
async def get_fake_data():
    layout = {
        "title": "Plot on [xxx]",
        "xaxis": {"title": "Time"},
        "yaxis": {"title": "Influencial events"},
    }
    traces = [
        {
            "x": [1, 2, 3, 4],
            "y": [10, 11, 12, 13],
            "type": "scatter",
            "mode": "lines+markers",
            "marker": {"size": [20, 40, 60, 80]},
            "name": "Trace 1",
        },
        {
            "x": [1, 2, 3, 4],
            "y": [14, 15, 13, 16],
            "type": "scatter",
            "mode": "markers",
            "name": "Trace 2",
        },
    ]
    return {"traces": traces, "layout": layout}


@app.get("/ask")
async def read_item(question: str | None = None):
    print("Got question:", question)
    # return {"question": question}  # test simple bounce back
    keywords = llm_complete_chat(
        messages=llm_construct_chat_keyword_gen(user_content=question),
        model="gpt-3.5-turbo",
    )
    print("Gen keywords:", keywords)
    return {"question": question, "kws": keywords.choices[0].message}


@app.get("/pull_news_via_bing", status_code=status.HTTP_200_OK)
async def pull_golden_news(count: int = 2):
    resp: BingSearchResp | None = get_news_bing(count=count)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    if resp is None:
        return {"success": False}
    print(resp)

    # TODO: store in DB

    return {
        "success": True,
        "bing_news_search_resp": resp.model_dump_json(),
    }

# queries = [“electric car OR charging station OR battery technology”, “BMW”, “Tesla”, “NIO”, “BYD”, “XPENG”, “CATL”]
@app.get("/proc_news_to_events")
async def proc_news(
    query: str,
    date: str,
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    db_query = {
        "published_date": {"$regex": f"^{date.strip()}"},
        "q": query.strip(),
    }
    print(db_query)
    results = col_nc_news.find(db_query)

    lst_nc_news = [NCNews(**doc) for doc in results]
    for nc_news in lst_nc_news:
        print(nc_news.query_str, nc_news.published_date)
    return {"n_records_found": len(lst_nc_news)}


@app.get("/pull_news_via_nc", status_code=status.HTTP_200_OK)
async def pull_golden_news(
    advanced_query: str = "electric vehicle",
    page_size: int = 5,
    page: int = 1,  # page * page_size = total count
    sources: str | None = None,  # if empty, use curated sources
    lang: str = "en",
    sort_by: str = "date",
    not_sources: str | None = None,
    from_datetime: str | None = None,  # "YYYY/mm/dd HH:MM:SS" in UTC
    to_datetime: str | None = None,
):
    if sources is None:
        sources = ",".join(CURATED_DATA_SOURCES)

    resp: NCSearchResp | None = get_news_nc(
        advanced_query=advanced_query,
        page_size=page_size,
        page=page,
        lang=lang,
        sort_by=sort_by,
        not_sources=not_sources,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        mongo_col_news=col_nc_news,
    )

    if resp is None:
        return {"success": False}

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(resp)
    col_nc_search_resp.insert_one(resp.model_dump())

    # TODO: store in DB

    return {
        "success": True,
        "nc_news_search_resp": resp.model_dump_json(),
    }
