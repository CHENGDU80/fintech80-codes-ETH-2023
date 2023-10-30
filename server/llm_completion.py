
# --- openAI
import os
import openai
from dotenv import load_dotenv


load_dotenv("./env_files/.env")
openai.api_key = os.getenv("OPENAI_API_KEY")


def llm_construct_chat_keyword_gen(
    user_content: str,
    system_content: str = (
        "You are a finance assistant, "
        "skilled in precisely listing short keywords related to the input question."
        "Use only solid industries and avoid simply adding words like 'Industry', 'Market', 'Stocks' to the stem."
    ),
    # # example
    # system_content: str = "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
):
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
            "Give a list search keywords (no more than 10), "
            f"which relate financially most importantly to this request: {user_content}"
        )},
    ]
    

def llm_complete_chat(
    messages: [str],
    model: str = "gpt-3.5-turbo",
):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    return completion


# anaylisys
def llm_gen_category_and_sentiment_score(
    user_content: str,
    aspects: [str] = ["policy", "cash flow", "interest rate", "tech innovation"],
    system_content: str = (
        "You are a finance assistant, skilled in categorizing a news into given aspects and analyzing the sentiment in each aspect."
        "Respond with a json object only, with aspects strings as keys and sentiment scores as values (-100 to 0 as bad view, 0 - 100 as good view)."
        "In addition 3 keys: industry, company, commodities. With the values being a list of tuples, first item the name, and second item the relatedness between 0.0 - 1.0. No more than 5 items in these 3 lists."
    ),
    # # example
    # system_content: str = "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
):
    tmp = "','".join(aspects)
    str_aspects = f"'{tmp}'"
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
            f"Analyze the content sentiments scores in these 4 fields: {str_aspects}\n"
            f"Given this news webpage abstract: {user_content}"
        )},
    ]