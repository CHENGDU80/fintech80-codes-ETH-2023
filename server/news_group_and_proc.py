import os
import json
from dotenv import load_dotenv

import cohere
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np
import random
import re
import string
import pandas as pd

from typing import Set

# local imports
from models import NCNews, Event
from llm_completion import llm_complete_chat, llm_summarize_event, llm_summarize_event_with_prev


# load bing env
load_dotenv("./env_files/.env")
_API_KEY = os.getenv("COHERE_API_KEY")


### Settings and constants for embeddings, clustering, distances
_COHERE_EMBEDDING_MODEL = "embed-english-v2.0"
_DUPLICATE_DISTANCE_THRES = 0.98
_N_CLUSTERS = 4

### Cohere client
cohere_client = cohere.Client(_API_KEY)


def nlp_preprocessing(text: str) -> str:
    """Clean up text before sending for embedding"""
    text = ''.join([c for c in text if ord(c) < 128])

    # Remove ASCII control characters
    text = ''.join([c for c in text if ord(c) > 31 and ord(c) < 128])

    # Remove and nbsp characters
    text = text.replace(' ', ' ')
    text = text.replace('nbsp', ' ')

    # Convert all uppercase letters to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove extra whitespace at the beginning and end of a line
    text = re.sub(r'^\s+|\s+$', '', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text


def create_batch_articles_embedding(lst_nc_news: [NCNews]) -> pd.DataFrame:
    """Load list of NCNews to 2 to cleaned titles and summary and  

    Args:
        lst_nc_news (NCNews]): the list of NCNews to be converted to Embedding and clustered

    Returns:
        pd.DataFrame: rows of record_id, title, summary, embedding
    """

    ids = []  # data record ID in mongoDB
    summaries = []
    titles = []
    for article in lst_nc_news:
        ids.append(str(article.id))
        titles.append(nlp_preprocessing(article.title))
        summaries.append(nlp_preprocessing(article.summary))

    # TODO: "Title {t} Content: {s}"
    emb_inputs = [f"{t} {s}" for t, s in zip(titles, summaries)]

    result = cohere_client.embed(
        input_type="clustering",
        texts=emb_inputs,
        model=_COHERE_EMBEDDING_MODEL,
    )

    df = pd.DataFrame({
        "record_id": ids,
        "title": titles,
        "summary": summaries,
        "embedding": result.embeddings,
    })
    return df


def cluster_on_embeddings(
    df: pd.DataFrame,
    n_clusters: int = _N_CLUSTERS,
    select_n_per_cluster: int = 1,
):
    """Remove duplicates, kmeans cluster

    Args:
        df (pd.DataFrame): see Returns in create_batch_articles_embedding(...)
    
    Returns:
        labels mapping between each embedding to a label
    """

    emb = df["embedding"].tolist()

    # drop duplicates based on embeddings
    distances = cosine_similarity(emb)
    print(f"Shape of cosine similarity distances: {distances.shape}")

    # get indices of pariwise embeddings that are too close
    indices = np.where(distances > _DUPLICATE_DISTANCE_THRES)
    # only keep non-diagonal, only need to keep row-ids
    dup_indices_set = set([i for i, j in zip(indices[0], indices[1]) if i != j])

    # get indices of unique articles
    unique_indices = list(set(range(df.shape[0])) - dup_indices_set)
    df_unique = df.iloc[unique_indices]
    print(f"After <duplicate removal>, shape of df_unique: {df_unique.shape}")

    emb_unique = df_unique["embedding"].tolist()
    # if not enough samples
    n_clusters = min(n_clusters, len(df_unique))
    # k-Means clustering
    kmean_model = KMeans(n_clusters=n_clusters, n_init="auto")
    labels = kmean_model.fit_predict(emb_unique)
    cluster_centroids = kmean_model.cluster_centers_

    # Sum of squared distances of samples to their closest cluster center, weighted by the sample weights if provided
    print(f"Inertial of kmeans on [{n_clusters}] clusters: {kmean_model.inertia_}")

    # save labels with the DF
    df_unique["label"] = labels

    # TODO: save tsne visualization?
    # tsne_visualization(embeddings=emb, cluster_labels=labels)

    return labels, cluster_centroids, df_unique


def tsne_visualization(embeddings, cluster_labels):
    tsne = TSNE(n_components=2, random_state=0)
    tsne_obj = tsne.fit_transform(np.array(embeddings))
    tsne_df = pd.DataFrame({'X':tsne_obj[:,0],
                            'Y':tsne_obj[:,1],
                            'cluster': cluster_labels})
    # print(tsne_df.head())
    tsne_df.plot.scatter(x = 'X', y = 'Y', c = 'cluster', colormap = 'viridis')


def test_new_article_similarity(
    existing_cluster_centroids,
    texts: [str] = ["We love Jason!"],
):
    emb = cohere_client.embed(
        input_type="clustering",
        texts=texts,
        model=_COHERE_EMBEDDING_MODEL,
    )

    dist_from_existing = cosine_similarity(
        existing_cluster_centroids,
        emb.embeddings,
    )

    return dist_from_existing


def cluster_get_main_and_multi_angle(
    df_unique_labeled: pd.DataFrame,
    labels_set: Set[int],
    n_multi_view: int = 3,  # number of additional different "views" within the same bigger cluster
    prev_events: list[Event] | None = None,
) -> dict[int, list[str]]:
    """Given all articles of date with labels, create different views in same cluster (combine them as the main event)

    Returns:
        
    """
    # To get the actual closest points from df
    selection = {}  # kcluster id => [record ids of selected multi-view articles],
    events = []

    for label in sorted(labels_set):
        selection[label] = []

        single_label_df = df_unique_labeled[df_unique_labeled["label"] == label]
        single_label_emb = single_label_df["embedding"].tolist()

        # # --- find "n_main_articles" closest to center, for ChatGPT to summarize
        # distances = cosine_similarity([centroid], single_label_emb)
        # closest_idx = np.argsort(distances, axis=1)[:, :n_main_articles]

        # closest_points = single_label_df.iloc[closest_idx[0]]
        # record_ids_closest_articles = closest_points['record_id'].tolist()
        # print(f"Record IDs of the closest points to cluster {label}: {record_ids_closest_articles}")
        # for rid in record_ids_closest_articles:
        #     print(f"Event [{label}] main: {single_label_df[single_label_df['record_id'] == rid]['title'].iloc[0]}")
        #     print()
        # selection[label]["main"] = record_ids_closest_articles

        # # remove main article(s) away
        # single_label_df = single_label_df[~single_label_df['record_id'].isin(record_ids_closest_articles)]
        # single_label_emb = single_label_df["embedding"].tolist()

        # --- Find multi-view articles
        # if not enough samples
        n_multi_view = min(n_multi_view, len(single_label_df))
        print("Performing clustering aiming to create n clusters:", n_multi_view)
        # sub clustering
        kmeans_sub = KMeans(n_clusters=n_multi_view, n_init=10)
        sub_labels = kmeans_sub.fit_predict(single_label_emb)
        sub_labels_set = set(sub_labels)
        print(f"Event [{label}] - number of sub labels (multi-angle): {len(sub_labels_set)} (among {len(single_label_df)} rows)")

        for sub_l in sorted(sub_labels_set):
            print(f"Event [{label}] - Sub-cluster [{sub_l}]")
            # randomly select an article from the sub-cluster
            # TODO: try find closest?
            record_id = random.choice(single_label_df[sub_labels == sub_l]["record_id"].tolist())
            print(f"Selected record <{record_id}>. Title: {single_label_df[single_label_df['record_id'] == record_id]['title'].iloc[0]}")

            selection[label].append(record_id)
        

        # summarize with GPT
        user_content = []
        for i, rid in enumerate(selection[label]):
            user_content.append(f"Article [{i}]:")
            tmp_df = single_label_df[single_label_df['record_id'] == rid]
            user_content.append(f"Title: {tmp_df['title'].iloc[0]}")
            user_content.append(f"Content: {tmp_df['summary'].iloc[0]}")
        str_user_content = "\n".join(user_content)
        if prev_events is not None:
            lst_prev_evs = [ev.ev_summary_short for ev in prev_events]
            gpt_resp = llm_complete_chat(messages=llm_summarize_event_with_prev(user_content=str_user_content, prev_events=lst_prev_evs), model="gpt-3.5-turbo-16k")
            try:
                json_resp = gpt_resp.choices[0].message["content"]
                obj_resp =json.loads(json_resp)
                ev_summary = obj_resp["event_summary"]
                ev_desc = obj_resp["event_description"]
                ev_matched = int(obj_resp["matched"])
            except Exception as e:
                print("Cannot load GPT response to event summary and description.")
                ev_summary = "Error response from GPT"
                ev_desc = "Error response from GPT"
                ev_matched = -1

            if ev_matched < 0 or ev_matched > len(prev_events):
                event = {'label': label, 'prev_ev_record_id': "", 'summary': ev_summary, 'description': ev_desc}
            else:
                event = {'label': label, 'prev_ev_record_id': (prev_events[ev_matched].id), 'summary': ev_summary, 'description': ev_desc}
        else:
            gpt_resp = llm_complete_chat(messages=llm_summarize_event(user_content=str_user_content), model="gpt-3.5-turbo-16k")
            try:
                json_resp = gpt_resp.choices[0].message["content"]
                obj_resp =json.loads(json_resp)
                ev_summary = obj_resp["event_summary"]
                ev_desc = obj_resp["event_description"]
            except Exception as e:
                print("Cannot load GPT response to event summary and description.")
                ev_summary = "Error response from GPT"
                ev_desc = "Error response from GPT"
            event = {'label': label, 'prev_ev_record_id': "", 'summary': ev_summary, 'description': ev_desc}

        events.append(event)
        print(f"Event [{label}] GPT summarization:\n{event}")

        print("\n\n")
    
    return selection, []


def _main():
    with open("test_data/news.json", "r") as f:
        data = json.load(f)
    
    dct_nc_news = {}
    for res in data["articles"]:
        news = NCNews(
            query_str="BYD",  # for ease of matching
            title=res["title"],
            author=res["author"],
            published_date=res["published_date"],
            published_date_precision=res["published_date_precision"],
            link=res["link"],
            clean_url=res["clean_url"],
            excerpt=res["excerpt"],
            summary=res["summary"],
            rights=res["rights"],
            rank=res["rank"],
            topic=res["topic"],
            country=res["country"],
            language=res["language"],
            authors=res["authors"],
            media=res["media"],
            is_opinion=res["is_opinion"],
            twitter_account=res["twitter_account"],
            match_score=res["_score"],
            api_entity_id=res["_id"],
            # parent search
            nc_search_id=str(""),
        )
        dct_nc_news[str(news.id)] = news
    
    df = create_batch_articles_embedding(lst_nc_news=dct_nc_news.values())
    labels, cluster_centroids, df_unique = cluster_on_embeddings(df=df)
    print("cluster_centroids" + "-" * 80)
    print(cluster_centroids)

    print("df_unique" + "-" * 80)
    print(df_unique)

    print("labels" + "-" * 80)
    print(labels)

    print("\n\n")

    selection = cluster_get_main_and_multi_angle(
        df_unique_labeled=df_unique,
        labels_set=set(labels.tolist()),
    )
    print("Article selection" + "-" * 80)
    print(selection)


if __name__ == "__main__":
    _main()
