from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# local import
from llm_completion import (
    llm_complete_chat,
    llm_construct_chat_keyword_gen,
)

from models import BingNews, BingSearchResp, Event, Company
from db_connections import db_conn_mongo, db_conn_redis
from fetch_news import get_news


### DB conn ####################################################################
# Mongo
col_company = db_conn_mongo.get_collection(database_name="main", collection_name="company")
col_event = db_conn_mongo.get_collection(database_name="main", collection_name="event")
col_bingnews = db_conn_mongo.get_collection(database_name="main", collection_name="bingnews")
col_bingsearchresp = db_conn_mongo.get_collection(database_name="main", collection_name="bingsearchresp")
# redis
rdb = db_conn_redis.get_rdb()

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

# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}

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


@app.get("/pull_golden_news")
async def pull_golden_news(count: int = 5):
    resp = get_news()
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(resp)
