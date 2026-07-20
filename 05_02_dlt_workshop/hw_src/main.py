import sys
from dotenv import load_dotenv
load_dotenv()

import logfire
logfire.configure()
logfire.instrument_pydantic_ai()

from agent import faq_agent, SearchDeps
from ingest import build_index, load_faq_data


def main(question):
    # Download the FAQ and build the search index
    documents = load_faq_data()
    index = build_index(documents)

    # Inject the index into the agent via the dependency container
    deps = SearchDeps(index=index)

    # Ask a question. run_sync blocks until the agent is done;
    # the agent may call search multiple times before answering.
    result = faq_agent.run_sync(question, deps=deps)

    print(result.output)


if __name__ == '__main__':
    script_name = sys.argv[0]
    if len(sys.argv) > 1:
        question = sys.argv[1]
        print(f"Question received: {question}")
    else:
        print("No question were provided. using the default")
        question = 'I just discovered the course. Can I join it?'
    print("============================")
    print("The answer")
    main(question)