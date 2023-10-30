from llm_completion import (
    llm_complete_chat,
    llm_gen_category_and_sentiment_score,
)
from datetime import datetime

def _main():
    with open("./test_data/article_test1.txt", 'r') as f:
        contents = f.read()

    # uncomment the following to supply the content manually, or use above to read web content from file
    # contents = (
    #     "Title: Tesla Faces Automated Driving Rival in Geely and Baidu EV\n"
    #     "Description/abstract: Competition is intensifying in China\u2019s automated-driving scene with the arrival of Jiyue 01, the first electric vehicle from a joint venture between Zhejiang Geely Holding Group Co. and Chinese search and tech giant Baidu Inc. "
    #     "By investing huge amount of copper, and lithium, we all win."
    # )
    
    # print(contents)
    file_ts = datetime.now().isoformat()

    resp = llm_complete_chat(messages=llm_gen_category_and_sentiment_score(user_content=contents))
    print(resp)
    with open(f"./test_data/resp_{file_ts}.json", 'w') as f:
        f.write(str(resp))
    with open(f"./test_data/resp_message_{file_ts}.json", 'w') as f:
        f.write(resp["choices"][0]["message"]["content"])


if __name__ == "__main__":
    _main()