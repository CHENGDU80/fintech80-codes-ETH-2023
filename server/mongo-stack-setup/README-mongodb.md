# planning course web

## How to run the stack

### Initial deployment of MongoDB

***IMPORTANT*** the env file should be `.env` file to be used by docker compose.

* Copy the `.mongodb.env.template` to a `.env` file and fill in the `[xxx]` fields
* Launch the containers
    ```bash
    docker compose -f docker-compose-mongo.yml up
    ```
* Inspect DBs
    * Navigate to http://0.0.0.0:8081 and use the `MONGO_EXPRESS_...` logins in the `.env` file to login

### How to connect to mongoDB via terminal and use mongosh

```
docker exec -it [container-name]-mongodb mongosh \
    --authenticationDatabase admin \
    -u root -p '$AUTH_PASSWD'
```

And perform actions such as
```
# ref: https://www.mongodb.com/docs/mongodb-shell/run-commands/
# check current DB
db
# use another DB
use XXX

# list collections
db.getCollectionNames()

# ref: https://www.mongodb.com/docs/manual/reference/method/db.collection.renameCollection/
# rename collection
# e.g. existing collection "col1"
db.col1.renameCollection([NEW_NAME])
```