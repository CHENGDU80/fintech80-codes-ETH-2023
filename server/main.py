from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from datetime import datetime, timedelta

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
from news_group_and_proc import (
    create_batch_articles_embedding,
    cluster_on_embeddings,
    cluster_get_main_and_multi_angle,
)


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
        "query_str": query.strip(),
    }
    print(f"DB query: {db_query}")
    results = col_nc_news.find(db_query)

    dct_nc_news = {}
    for doc in results:
        nc_news = NCNews.model_validate(doc)
        dct_nc_news[str(nc_news.id)] = nc_news

    for nc_news in dct_nc_news.values():
        print(nc_news.query_str, nc_news.published_date)

    # --- search DB for previous events on same query_str and prev date
    curr_day = datetime.strptime(date, '%Y-%m-%d')
    prev_day = curr_day - timedelta(days=1)
    prev_day_str = prev_day.strftime('%Y-%m-%d')

    db_query_prev_evs = {
        "for_date": {"$regex": f"^{date.strip()}"},
        "company_ids": query.strip(),
    }

    lst_prev_events = []
    res_prev_evs = col_event.find(db_query_prev_evs)
    for doc in res_prev_evs:
        ev = Event.model_validate(doc)
        lst_prev_events.append(ev)

    # --- process to get events
    df = create_batch_articles_embedding(lst_nc_news=dct_nc_news.values())
    labels, cluster_centroids, df_unique = cluster_on_embeddings(df=df)
    print("cluster_centroids" + "-" * 80)
    print(cluster_centroids)

    print("df_unique.head" + "-" * 80)
    print(df_unique.head())

    print("labels" + "-" * 80)
    print(labels)
    print()

    selection, events = cluster_get_main_and_multi_angle(
        df_unique_labeled=df_unique,
        labels_set=set(labels.tolist()),
    )
    print("Article selection" + "-" * 80)
    print(selection)

    # create events
    lst_ev_ids = []
    for ev in events:
        event = Event(
            for_date=date,
            ev_description=ev["description"],
            ev_summary_short=ev["summary"],
            previous_event_id=ev["prev_ev_record_id"],
            core_news_ids=selection[ev["label"]],
            # propagate later
            ev_infl_tech=0.0,
            ev_infl_fin=0.0,
            ev_infl_policy=0.0,
            ev_infl_combined=0.0,
            company_ids=[query],
            company_relevances=[1.0],
        )
        col_event.insert_one(event.model_dump())
        lst_ev_ids.append(str(event.id))

    return {
        "records_found": {
            "num": len(dct_nc_news),
            "ids": dct_nc_news.values(),
        },
        "prev_evs": lst_prev_events,
        "events_inserted": {
            "num": len(events),
            "ids": lst_ev_ids,
        },
    }


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
