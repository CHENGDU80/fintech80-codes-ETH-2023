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
# --reload changes on save, disable in final deployment
# 0.0.0.0 to make it public
# may need to use port 80 for http in final, or docker map port

uvicorn main:app --reload --host 0.0.0.0 --port 1234
```

#### Side note on `.env` loading (Skip if you know how they work)
Refer to the parts of code where these are used to see how to use `.env` files

```python
load_dotenv(path_to_env_file)
os.environ.get("ENV_VAR_KEY", default_val)
```

## Maintainer

Ask Jason


# Other
### PORTs available on server
60-9000

### Focus list
Tesla 特斯拉 (US)
BMW 宝马 (DE)
Audi 奥迪 (DE)
Ford 福特(US)
Porsche 保时捷 (DE)
iMiEV 三菱 (JP)
BYD 比亚迪 (CN)
(maybe)
CTL 宁德时代 (CN)
Xpeng Motor 小鹏汽车
Nio 蔚来

### Ref links

#### Bing NewsSearch API
* API general: https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/response-objects#newsarticle
* params: https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/query-parameters#news-categories-by-market
* advanced query: https://support.microsoft.com/en-us/topic/advanced-search-options-b92e25f1-0085-4271-bdf9-14aaea720930
  * https://support.microsoft.com/en-us/topic/advanced-search-keywords-ea595928-5d63-4a0b-9c6b-0b769865e78a


#### Alternative news sources
* https://stockanalysis.com/stocks/


#### OpenAI API
* Embedding: https://platform.openai.com/docs/guides/embeddings/use-cases
* Web QA tutorial (tokenize, embeddings, knowledge base): https://platform.openai.com/docs/tutorials/web-qa-embeddings
* Multi-agent with LangChain: https://blog.langchain.dev/gpteam-a-multi-agent-simulation/