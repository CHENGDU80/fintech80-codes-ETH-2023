from pydantic_settings import BaseSettings
import redis
import pymongo
from pymongo.collection import Collection


class Settings(BaseSettings):
    mongo_dsn: str
    redis_auth: str
    class Config:
        env_file = "./env_files/.dbs.env"
        env_file_encoding = "utf-8"


class RedisConn:
    def __init__(self, redis_auth: str) -> None:
        self._conn = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            password=redis_auth,
            charset="utf-8",
            decode_responses=True,
        )
        if not self._conn.ping():
            print("Cannot connect to REDIS. Abort.")
            exit(1)
        else:
            print("Connected to REDIS")

    def get_rdb(self):
        return self._conn


# mongoDB clients
class MongoConn:
    def __init__(self, dsn: str) -> None:
        try:
            self._client = pymongo.MongoClient(dsn, serverSelectionTimeoutMS=5000)
            print(self._client.server_info())
            print("Connected to DB. Entering main loop...")
        except Exception as e:
            print(f"Error: Unable to connect to MongoDB: {e}")
            exit(1)

    def get_collection(self, database_name: str, collection_name: str):
        # return if exists, otherwise create
        db = self._client[database_name]
        collection: Collection = db[collection_name]
        return collection


_settings = Settings()
db_conn_mongo = MongoConn(dsn=_settings.mongo_dsn)
db_conn_redis = RedisConn(redis_auth=_settings.redis_auth)
