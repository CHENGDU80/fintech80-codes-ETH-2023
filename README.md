[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/ZEqMxGpP)



# Server / API part

## How to setup

Enter venv
```
# needed first time
python3 -m venv venv

# needed each time
source venv/bin/activate

# needed first time
pip3 install -U pip

# needed each time when lib list updated
pip3 install -r requirements.txt
```

## How to run backend (mono)

### Setup env file(s)
Copy the `*.env.template` files to  `*.env` files and fill out the fields

### Run
```
uvicorn main:app \
    --reload        # reload changes on save, disable in final deployment
    --host 0.0.0.0  # to make it public
    --port 1234     # may need to use port 80 for http in final, or docker map port
```

#### Side note on `.env` loading (Skip if you know how they work)
Refer to the parts of code where these are used to see how to use `.env` files

```python
load_dotenv(path_to_env_file)
os.environ.get("ENV_VAR_KEY", default_val)
```

## Maintainer

Ask Jason
