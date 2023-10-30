import openai
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY
def llm_complete_chat(
    messages: [str],
    model: str = "gpt-3.5-turbo",
):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    return completion.choices[0].message.content


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
def llm_sum_golden_news(
    news_title: str,
    description: str,
    system_content: str = (
    """
    TASK: When the user gives a NEWS TITLE and its DESCRIPTION, identify the event this news talks about. Summarize the event very clearly in to 10 keywords. Pay more attention to the NEWS TITLE than the DESCRIPTION. Examples for some keywords are: company names, technologies
    RESPONSE: the event.
    
    """ 
    """
    Instruction: perform the TASK carefully, respond only the RESPONSE.
    """
    """
    NOTE: The user input consists of list of NEWS TITLES, list of DESCRIPTION. The summarization should pay more attention to the NEWS TITLE and use DESCRIPTION as supplement. 
    """
        
        
    )
):
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": 
            f"This is the NEWS TITLE: {news_title}; this is the DESCRIPTION: {description}."
        },
    ]
def llm_multi_angle_analysis(
    news_titles,
    description_list,
    event: str,
    system_content: str = (
    """
    TASK: When the user gives a list of NEWS TITLES, their respective DESCRIPTION, and an EVENT, predict whether the newses describe the EVENT.
    RESPONSE: respond a valid JSON with the NEWS TITLES as the keys and yes or no as values.
    
    """ 
    """
    Instruction: perform the TASK carefully, respond only what is described in the RESPONSE.
    """
    
    """
    NOTE: The user input consists of list of NEWS TITLES, list of DESCRIPTION, and EVENT. It is okay if none of the NEWS TITLES describes the EVENT
    """
        
        
    )
):
    return[
        {"role": "system", "content": system_content},
        {"role": "user", "content": 
            f"This is the NEWS TITLES: {news_titles}; this is the DESCRIPTION: {description_list}; this is the EVENT: {event}."
        },
    ]