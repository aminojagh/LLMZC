import sys

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

from data.ingest import load_faq_data
from data.index import build_index
from rag_helper import RAGBase


def create_assistant(
    instructions,
    prompt_template
):
    load_dotenv()

    documents = load_faq_data()
    index = build_index(documents)

    return RAGBase(
        index=index,
        llm_client=OpenAI(),
        instructions = instructions,
        prompt_template = prompt_template,
    )


if __name__ == "__main__":
    
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    print(f"templates_dir: {templates_dir}")
    with open(templates_dir / "instructions.txt", "r") as file:
        instructions = file.read().strip()
    with open(templates_dir / "prompt_template.txt", "r") as file:
        prompt_template = file.read().strip()
    

    query = "How do I join the course?"
    if len(sys.argv) > 1:
        query = sys.argv[1]

    print(f"query: {query}")

    # assistant = create_assistant(instructions, prompt_template)
    # answer = assistant.rag(query)
    # print(answer)