import datetime

from bson.objectid import ObjectId
from pydantic import (
    BaseModel,
    Field,
    GetJsonSchemaHandler,
)
from pydantic_core import CoreSchema
from typing import Any, List

"""
Notes:
* fields that use default or default_factory mean that it could be missing upon init.
"""


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
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type="string")
        return json_schema


class BingSearchResp(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    query_params: str  # json
    metadata: str # json
    news_ids: List[str] = Field(default_factory=list)  # BingNews

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


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
    summary: str = Field(default_factory=str)
    infl_tech: float = Field(default_factory=float)
    infl_fin: float = Field(default_factory=float)
    infl_policy: float = Field(default_factory=float)

    # reverse link to parent categories
    # BingSearchResp
    bing_search_id: str
    # Event
    event_group_id: str = Field(default_factory=str)

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        populate_by_name = True


class NCSearchResp(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    query_str: str
    status: str
    total_hits: int
    page: int
    total_pages: int
    page_size: int

    news_ids: List[str] = Field(default_factory=list)  # NCNews

    user_input: str  # json

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class NCNews(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    query_str: str  # for ease of direct filter
    title: str
    author: str
    published_date: str
    published_date_precision: str
    link: str
    clean_url: str
    excerpt: str | None
    summary: str
    rights: str
    rank: int  # TODO: optional?
    topic: str
    country: str
    language: str
    authors: str
    media: str
    is_opinion: bool
    twitter_account: str | None
    match_score: float  # higher better
    api_entity_id: str

    # processed output
    ai_summary: str = Field(default_factory=str)
    infl_tech: float = Field(default_factory=float)
    infl_fin: float = Field(default_factory=float)
    infl_policy: float = Field(default_factory=float)

    # reverse link to parent categories
    # NCSearchResp
    nc_search_id: str
    # Event
    event_group_id: str = Field(default_factory=str)

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        populate_by_name = True


class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    ev_infl_tech: float
    ev_infl_fin: float
    ev_infl_policy: float
    ev_summary: str  # short, but several sentences
    ev_summary_short: str  # one line, headline style, for gpt too

    create_ts: str = Field(default=datetime.datetime.now().isoformat())
    update_ts: str = Field(default=datetime.datetime.now().isoformat())

    bing_news_ids: List[str] = Field(default_factory=list)
    nc_news_ids: List[str] = Field(default_factory=list)  # the news in the same cluster (probably won't do it)
    core_news_ids: List[str] = Field(default_factory=list)  # the news IDs used to generate the summary and description
    previous_event_id: str | None = Field(default=None)  # if can be linked to a prev day's event

    company_ids: List[str] = Field(default_factory=list)
    company_relevances: List[float] = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        populate_by_name = True


class Company(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    primary_industry: str  # TODO: also entity?
    event_ids: List[str]= Field(default_factory=list)
    event_relevances: List[float] = Field(default_factory=list)

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

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        populate_by_name = True


class Commodity(BaseModel):
    """"""

class Industry(BaseModel):
    """"""