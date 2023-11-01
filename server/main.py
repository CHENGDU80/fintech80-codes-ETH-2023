from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from bson.objectid import ObjectId

from datetime import datetime, timedelta

# local import
from llm_completion import (
    llm_complete_chat,
    llm_construct_chat_keyword_gen,
    llm_gen_category_and_sentiment_score,
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
    # Dummy data test
    dct = {"1": 1, "2": 2, "3": 3}
    lst1 = [1,2,3]
    events = ['a', 'b']
    lst2 = ['x', 'y']
    return {
        "records_found": {
            "num": len(dct),
            "ids": list(dct.keys()),
        },
        "prev_evs": len(lst1),
        "events_inserted": {
            "num": len(events),
            "ids": lst2,
        },
    }

@app.get("/sample_plot_data")
async def plotly_sample_data():
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


@app.get("/analyze_article")
async def summarize_article(question: str | None = None):
    # return {"question": question}  # test simple bounce back
    result = llm_complete_chat(
        messages=llm_gen_category_and_sentiment_score(user_content=question),
        model="gpt-3.5-turbo-16k",
    )
    return {"Input": question, "Analysis": result.choices[0].message}


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
        "for_date": {"$regex": f"^{prev_day_str.strip()}"},
        "company_ids": query.strip(),
    }

    lst_prev_events = []
    res_prev_evs = col_event.find(db_query_prev_evs)
    for doc in res_prev_evs:
        ev = Event.model_validate(doc)
        lst_prev_events.append(ev)
        print(f"Prev event ID: {str(ev.id)}")

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

    if len(lst_prev_events) >0:
        selection, events = cluster_get_main_and_multi_angle(
            df_unique_labeled=df_unique,
            labels_set=set(labels.tolist()),
            prev_events=lst_prev_events,
        )
    else:
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
            previous_event_id=str(ev["prev_ev_record_id"]),
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
            "ids": list(dct_nc_news.keys()),
        },
        "prev_evs": len(lst_prev_events),
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


# --- for passing data to front end
@app.get("/api/events")
async def fetch_events(
    target_entity: str,  # e.g. company name
    date_start: str,
    date_end: str,
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    db_query = {
        "for_date": {"$gte": date_start, "$lte": date_end},
        "company_ids": target_entity,
    }

    print(f"DB query: {db_query}")
    results = col_event.find(db_query)

    dct_evs = {}
    for doc in results:
        ev = Event.model_validate(doc)
        dct_evs[str(ev.id)] = ev

    res = [ev.model_dump_json() for ev in dct_evs.values()]

    # update scores of all events based on related core_news
    for eid, ev in dct_evs.items():
        res_lst_news = await fetch_lst_news_by_event_id(event_id=eid, token=token)
        lst_news_jsons = res_lst_news["object_json"]
        lst_news = [NCNews.model_validate_json(tmp) for tmp in lst_news_jsons]
        num_news = float(len(lst_news))
        # calculate avg scores and write to the event
        ev_infl_tech = sum([n.infl_tech for n in lst_news]) / num_news
        ev_infl_fin = sum([n.infl_fin for n in lst_news]) / num_news
        ev_infl_policy = sum([n.infl_policy for n in lst_news]) / num_news

        ev_infl_combined = ev_infl_tech + ev_infl_fin + ev_infl_policy

        col_event.update_one(
            {"_id": ev.id},
            {
                "$set": {
                    "ev_infl_tech": ev_infl_tech,
                    "ev_infl_fin": ev_infl_fin,
                    "ev_infl_policy": ev_infl_policy,
                    "ev_infl_combined": ev_infl_combined,
                }
            }
        )

    # query again for updated data
    results = col_event.find(db_query)

    dct_evs = {}
    for doc in results:
        ev = Event.model_validate(doc)
        dct_evs[str(ev.id)] = ev

    res = [ev.model_dump_json() for ev in dct_evs.values()]

    return {
        "success": True,
        "summary": {
            "number": len(dct_evs),
            "event_ids": list(dct_evs.keys()),
        },
        "event_object_jsons": res,
    }


@app.get("/api/event_by_id")
async def fetch_event_by_id(
    event_id: str,  # DB id of the news document
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    db_query = {"_id": ObjectId(event_id)}
    print(f"DB query: {db_query}")
    res = col_event.find_one(db_query)
    if res is None:
        return {"Succsss": False}
    
    ev = Event.model_validate(res)
    return {
        "success": True,
        "summary": {
            "number": 1,
            "event_id": str(ev.id),
        },
        "object_json": ev.model_dump_json(),
    }
        

@app.get("/api/lst_news_by_event_id")
async def fetch_lst_news_by_event_id(
    event_id: str,  # DB id of the news document
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    ev_res = await fetch_event_by_id(event_id=event_id, token=token)
    if ev_res["success"] is False:
        return {"success": False}

    ev = Event.model_validate_json(ev_res["object_json"])
    dct_news = {}
    for nid in ev.core_news_ids:
        res = await fetch_news_by_id(news_id=nid, token=token)
        if res["success"]:
            news = NCNews.model_validate_json(res["object_json"])
            dct_news[str(news.id)] = news.model_dump_json()
    return {
        "success": True,
        "summary": {
            "number": len(dct_news),
            "news_ids": list(dct_news.keys()),
        },
        "object_json": list(dct_news.values()),
    }


@app.get("/api/news_by_id")
async def fetch_news_by_id(
    news_id: str,  # DB id of the news document
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    db_query = {"_id": ObjectId(news_id)}

    print(f"DB query: {db_query}")
    res = col_nc_news.find_one(db_query)

    if res is None:
        return {"success": False}

    news = NCNews.model_validate(res)
    return {
        "success": True,
        "summary": {
            "number": 1,
            "event_id": str(news.id),
        },
        "object_json": news.model_dump_json(),
    }


@app.get("/api/company_data")
async def update_company_data(
    target_entity: str,  # e.g. company/topic name,
    token: str | None = None,
):
    if token is None or token != SIMPLE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # see if there is one, if not, create and follow the update procedure
    company_query = {"company_name": target_entity}
    if not col_company.find_one(company_query):
        company = Company(
            company_name=target_entity,
            primary_industry="EV",
            score_tech=0.0,
            score_fin=0.0,
            score_policy=0.0,
            c0=0.0,
            c_tech=0.33,
            c_fin=0.33,
            c_policy=0.33,
            score_combined=0.0,
        )
        col_company.insert_one(company.model_dump())
    
    company = Company.model_validate(col_company.find_one(company_query))

    # fetch related events and update score
    res = await fetch_events(
        target_entity=target_entity,
        # all events
        date_start="2022-01-01",
        date_end="2024-10-10",
        token=token,
    )

    ev_ids = res["summary"]["event_ids"]
    lst_company_events = []
    for eid in ev_ids:
        res = await fetch_event_by_id(event_id=eid, token=token)
        if res["success"]:
            lst_company_events.append(Event.model_validate_json(res["object_json"]))
    
    # just clear all event entries
    company.score_tech = 0.0
    company.score_fin = 0.0
    company.score_policy = 0.0
    company.event_ids = []
    company.lst_score_tech = []
    company.lst_score_fin = []
    company.lst_score_policy = []
    company.score_combined = 0.0

    sorted_lst_events: list[Event] = sorted(lst_company_events, key=lambda ev: ev.for_date)
    for ev in sorted_lst_events:
        # if str(ev.id) not in company.event_ids:
        # add the new event id and respective score
        company.event_ids.append(str(ev.id))
        company.score_tech += ev.ev_infl_tech
        company.score_fin += ev.ev_infl_fin
        company.score_policy += ev.ev_infl_policy
        company.lst_score_tech.append(company.score_tech)
        company.lst_score_fin.append(company.score_fin)
        company.lst_score_policy.append(company.score_policy)

    # print(company.lst_score_fin)

    def calc_company_score(comp: Company, s_t, s_f, s_p):
        return comp.c0 + comp.c_tech * s_t + comp.c_fin * s_f + comp.c_policy * s_p

    company.score_combined = calc_company_score(
        comp=company,
        s_t=company.score_tech,
        s_f=company.score_fin,
        s_p=company.score_policy,
    )

    # update score
    col_company.update_one(
        company_query,
        {
            "$set": {
                "score_tech": company.score_tech,
                "score_fin": company.score_fin,
                "score_policy": company.score_policy,
                "event_ids": company.event_ids,
                "lst_score_tech": company.lst_score_tech,
                "lst_score_fin": company.lst_score_fin,
                "lst_score_policy": company.lst_score_policy,
                "score_combined": company.score_combined,
            }
        }
    )

    # retrieve one more time for return
    ret = Company.model_validate(
        col_company.find_one(company_query),
    )
    # compute extra list of total score changes
    hist_score_combined = []
    for idx, ev in enumerate(sorted_lst_events):
        s_t = company.lst_score_tech[idx]
        s_f = company.lst_score_fin[idx]
        s_p = company.lst_score_policy[idx]
        sc = calc_company_score(ret, s_t, s_f, s_p)
        # print(ev.id, sc)
        hist_score_combined.append((ev.for_date, sc))

    # handle duplicate date
    date_count = {}
    new_lst = []

    for t in hist_score_combined:
        date, value = t
        dt = datetime.strptime(date, "%Y-%m-%d")
        
        # Check for duplicates and increment counter
        if date in date_count:
            date_count[date] += 1
            dt += timedelta(seconds=date_count[date])  # Add minor time diff (in seconds)
        else:
            date_count[date] = 0
        
        # Convert datetime back to string and append to new list
        new_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        new_lst.append((new_date, value))

    return {
        "success": True,
        "summary": {
            "number": 1,
            "company_id": str(ret.id),
        },
        "hist_score_combined_by_date": new_lst,
        "object_json": ret.model_dump_json(),
    }
