import requests
from minsearch import Index
from sqlitesearch import TextSearchIndex
from tqdm.auto import tqdm

def load_faq_data():
    docs_url = "https://datatalks.club/faq/json/courses.json"
    response = requests.get(docs_url)
    courses_raw = response.json()

    documents = []
    url_prefix = "https://datatalks.club/faq"

    for course in courses_raw:
        course_url = f"""{url_prefix}{course["path"]}"""
        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_data = course_response.json()

        documents.extend(course_data)

    return documents

def build_index(documents):
    index = Index(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"]
    )
    index.fit(documents)
    return index


def build_sqlite_index(docs: str, db_path: str):

    index = TextSearchIndex(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"],
        db_path=db_path
    )

    for doc in tqdm(docs, total=len(docs), desc="Processing Documents..."):
        index.add(doc)

    index.close()
    print(f"Done. Index saved to {db_path}")