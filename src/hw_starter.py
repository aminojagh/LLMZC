"""Starter code for the monitoring homework.

Sets up the text-search RAG from homework 1 and a shared OpenAI client.
"""

from openai import OpenAI
from pathlib import Path
from gitsource import GithubRepositoryDataReader
from minsearch import Index
from src.rag_helper import GitRAG

COMMIT = "8c1834d"

templates_dir = Path(__file__).resolve().parent.parent / "templates"
with open(templates_dir / "homework_01_instructions.txt", "r") as file:
    instructions = file.read().strip()
with open(templates_dir / "prompt_template.txt", "r") as file:
    prompt_template = file.read().strip()


# --- Load the course lessons (same as HW1, HW2, HW4) ---
reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id=COMMIT,
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)
documents = [file.parse() for file in reader.read()]

index = Index(text_fields=["content"], keyword_fields=["filename"])
index.fit(documents)

client = OpenAI()
rag = GitRAG(
    index=index,
    llm_client=client,
    instructions=instructions,
    prompt_template=prompt_template
)

if __name__ == "__main__":
    query = "How does the agentic loop keep calling the model until it stops?"
    answer = rag.rag(query)
    print(answer)
