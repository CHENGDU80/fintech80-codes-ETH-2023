import datetime

from bson.objectid import ObjectId
from pydantic import (
    BaseModel,
    Field,
)
from typing import List


### Models #####################################################################
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BingSearchResp(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    query_params: str  # json
    metadata: str # json
    news_ids: [str] = Field(default_factory=list)  # BingNews

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class BingNews(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    name: str
    url: str
    image: str  # json
    description: str
    about: str # json
    provider: str # json for now, contains important info like type and name of organization
    date_publised: str = Field(default=datetime.datetime.now().isoformat())

    # processed output
    summary: str
    infl_tech: float
    infl_fin: float
    infl_policy: float

    # reverse link to parent categories
    bing_search_id: str  # BingSearchResp
    event_group: "Event"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    ev_infl_tech: float
    ev_infl_fin: float
    ev_infl_policy: float
    ev_summary: str  # short, but several sentences
    ev_summary_short: str  # one line, headline style

    create_ts: str = Field(default=datetime.datetime.now().isoformat())
    update_ts: str = Field(default=datetime.datetime.now().isoformat())

    bing_news: ["BingNews"] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Company(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    primary_industry: str  # TODO: also entity?
    events: ["Event"]= Field(default_factory=list)

    # TODO: what are the initial values based on? Or do we care only about the derivatives
    score_tech: float
    score_fin: float
    score_policy: float

    # assume linear regression
    c0: float
    c_tech: float
    c_fin: float
    c_policy: float

    # s_c = c0 + c1 * s1 + c2 * s2 + ...
    score_combined: float


class Commodity(BaseModel):
    """"""

class Industry(BaseModel):
    """"""