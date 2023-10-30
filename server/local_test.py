from llm_completion import (
    llm_complete_chat,
    llm_gen_category_and_sentiment_score,
)

def _main():
    with open("./test_data/article_test0.txt", 'r') as f:
        contents = f.read()
    
    # print(contents)
    resp = llm_complete_chat(messages=llm_gen_category_and_sentiment_score(user_content=contents))
    print(resp)
    with open("./test_data/resp.json", 'w') as f:
        f.write(str(resp))
    with open("./test_data/resp_message.json", 'w') as f:
        f.write(resp["choices"][0]["message"]["content"])


if __name__ == "__main__":
    _main()