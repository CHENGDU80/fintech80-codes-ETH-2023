from fastapi import FastAPI

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


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


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