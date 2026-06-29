from minsearch import Index
from sqlitesearch import TextSearchIndex
from tqdm.auto import tqdm


def build_index(
        documents,
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"]
):
    index = Index(
        text_fields=text_fields,
        keyword_fields=keyword_fields
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