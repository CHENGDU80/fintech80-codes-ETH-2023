from fastapi import FastAPI

# local import
from llm_completion import (
    llm_complete_chat,
    llm_construct_chat_keyword_gen,
)


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