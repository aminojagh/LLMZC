class RAGBase:
    def __init__(
        self,
        index,
        # The index parameter is anything with a search method,
        # whether minsearch, sqlitesearch, or something else.
        llm_client,
        instructions,
        prompt_template,
        model="gpt-5.4-mini",
        search_boost_dict = {"question": 3.0, "section": 0.5},
        search_filter_dict = {"course": "llm-zoomcamp"}
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model
        self.search_boost_dict = search_boost_dict
        self.search_filter_dict = search_filter_dict

    def search(self, query, num_results=5):
        boost_dict = self.search_boost_dict
        filter_dict = self.search_filter_dict

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )
    
    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc["section"])
            lines.append("Q: " + doc["question"])
            lines.append("A: " + doc["answer"])
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )
    
    def llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response
    
    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer
    

class GitRAG(RAGBase):
    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append("filename: " + doc["filename"])
            lines.append("content: " + doc["content"])
            lines.append("="*30)

        return "\n".join(lines).strip()