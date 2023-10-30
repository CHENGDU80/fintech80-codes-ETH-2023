# Start the Redis database and Redisinsight web GUI

This only needs to setup once and is shared between staging and production env.

#### Launch the stack

First, create the `.env` file by copying from the `.env.redis.template` in this folder, and fill-out the values.

Then: `docker compose up -d`

#### Connect with cli
```
docker exec -it redis-stack-server redis-cli -a $PASSWD
```
where the `$PASSWD` is the `$REDIS_AUTH` in the `.env` file

##### To restore the contents to a new instance
```
docker exec -it redis-stack bash
# redis-cli -a $PASSWD --pipe < [/path/to]/appendonly.aof
```

#### Use the redis-py
* In the parent folder (`py_server`)
* Create a `.redis.env` file, and put the same pw as above commands
    ```bash
    REDIS_AUTH=[xxx]
    ```
* Check connection by `python3 redis_db.py`

### Ref docker cmd to launch

This was initially used to start the stack. But the redisDB and the Redisinsight GUI are launched in the same container, which made it hard to restart a single service. Then the `docker-compose` is used.

#### (deprecated) Launch the stack

```bash
docker run -d --name redis-stack -p 6379:6379 -v [path_to/]data:/data -e REDIS_ARGS="--requirepass $PASSWD" -e RIAUTHPROMPT=1 -e RIAUTHTIMER=30 -p 8001:8001 redis/redis-stack:latest
```

