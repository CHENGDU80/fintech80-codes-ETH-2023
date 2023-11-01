
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


# summarize event
def llm_summarize_event(
    user_content: str,
    system_content: str = (
        "You are a finance assistant, skilled in combining news and find what's in common (identify key event)"
        "Respond with a json object only, with key 'event_summary' with a short sentence (no more than 20 words),"
        "and key 'event_description' with a slightly longer exerpt introducing the event and giving an explanation how the news are considered the same event (less than 80 words)."
    ),
):
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
            f"Analyze the content from these different news articles and summarize them to a common event. Here're the news articles {user_content}\n"
        )},
    ]


# summarize event but try to link to previous
def llm_summarize_event_with_prev(
    user_content: str,
    prev_events: list[str],
    system_content: str = (
        "You are a finance assistant, skilled in combining news and find what's in common (identify key event)."
        "Given a list of strings describing previous events, and 3 new articles, try to match if the 3 new news articles all belong to the same event."
        "If so, return json object, with key 'matched' to the list index of the prev_event (starting 0), and the following:"
        "key 'event_summary' with a short sentence (no more than 20 words) which would be very similar to the previous event, but includes the new article changes."
        "and key 'event_description' with a slightly longer exerpt introducing the event and giving an explanation how the news are considered the same event (less than 80 words)."
        "If they do not appear to be follow-up or related to the same previous event, return a json object with key 'matched' to -1 and "
        "key 'event_summary' on just the new articles, and key 'event_description' with the same functionality."
    ),
):
    str_evs = ", ".join(prev_events)
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
            f"Analyze the content from these different news articles and see if they could be categorized to a previous key event among [{str_evs}]"
            f"Either link them to a common event or summarize them to a new event. Here're the news articles {user_content}\n"
        )},
    ]

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




# import openai

# openai.api_key = "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"


# from tqdm import tqdm


# for i, d in tqdm(df_unique.iterrows()):
#     if i == 0:
#         continue
#     text = d["article"]
#     title = d["title"]

#     system_content: str = ("""TASKS: 
#     1.When the user provides TEXT and TITLE, summarize them very clearly in 50 words. Pay both attention to the TEXT and the TITLE.
#     2.Analyze the relevance scores of the TEXT in these 3 aspects: TECHNOLOGY, FINANCE, POLICY.
#     3.Analyze the sentiments scores of the TEXT in these 3 aspects: TECHNOLOGY, FINANCE, POLICY.
#     4.Respond with a json object only, with Summary, Technology, Finance, Policy as keys, the summary and a dictionary of relevance scores (float, from 0.0 as Not Relevant to 1.0 as Strongly Relevant) and sentiment scores (int, -1 as Negative, 0 as Neutral, and 1 as Positive) as values.

#     """ 
#     """
#     Instruction:  
#     Here is a sample TITLE: Chery Accelerates EV Technology Advancements Amid Financial Crunch
#     Here is a sample TEXT: Chery announces a comprehensive technological transformation plan aimed at enhancing their electric vehicle (EV) offerings. This may include advancements in battery technology and sustainable energy solutions.While embarking on these technological improvements and workforce development initiatives, Chery acknowledges a short-term finance shortage. The company is actively exploring cost-saving measures to address this challenge.In response to Chery's efforts, the government announces new policy support to incentivize and facilitate the transition to technologies.
#     Here is a sample response with summary and scores: {"Summary": "Chery unveils a thorough tech transformation plan to bolster its electric vehicle (EV) segment, encompassing battery technology upgrades and sustainable energy solutions. Despite facing a short-term financial deficit, Chery is adopting cost-saving strategies. In support, the government introduces policies incentivizing this technological shift, aiding Chery's transition journey.", "Technology": {"relevance": 0.8, "sentiment": 1}, "Finance": {"relevance": 0.6, "sentiment": -1}, "Policy": {"relevance": 0.9, "sentiment": 1}}
#     Here are some keywords from the TEXT that lead to the sample scores: Technology: "technological transformation",  "advancement", "battery"; Finance:"finance shortage", "challenge"; Policy:"government", "policy", "incentivize";
#     """)



#     inst = [
#         {"role": "system", "content": system_content},
#         {"role": "user", "content": (
#             f"Analyze the relevance score and sentiment score in these 3 fields: 'Technology', 'Finance', 'Policy'\n"
#             f"Given this news TEXT: {text} and this news TITLE: {title}"
#         )},
#     ]

#     resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=inst)

#     try:
#         with open("data/articles/" + str(i) + ".json", "w") as f:
#             json.dump(json.loads(resp.choices[0].message.content), f)
#     except:
#         print("error")
#         print(resp.choices[0].message.content)
#         print()



# resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=inst)


# json.loads(resp.choices[0].message.content)