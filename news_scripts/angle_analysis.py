from process_text import llm_complete_chat, llm_gen_category_and_sentiment_score, llm_sum_golden_news, llm_multi_angle_analysis
from get_news import get_golden_news, get_normal_news
import json
import os
from tqdm import tqdm
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

golden_news = get_golden_news()[0]
title = golden_news["title"]
description = golden_news["description"]
event=llm_complete_chat(llm_sum_golden_news(title,description))

normal_news = get_normal_news(event)
titles = ';'.join([item["title"] for item in normal_news])
descriptions = ';'.join([item["description"] for item in normal_news])
print(titles)
analysis=llm_complete_chat(llm_multi_angle_analysis(titles, descriptions, event))

print(event)
print(analysis)