from .utils import vec_to_str


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
        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=self.search_boost_dict,
            filter_dict=self.search_filter_dict
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
    


class RAGVector(RAGBase):
    def __init__(self, embedder, **kwargs):
        super().__init__(**kwargs)
        self.embedder = embedder

    def search(self, query, num_results=5):
        query_vector = self.embedder.encode(query)

        return self.index.search(
            query_vector,
            num_results=num_results,
            filter_dict=self.search_filter_dict
        )




class RAGPgVector(RAGBase):
    def __init__(self, embedder, conn, course = "llm-zoomcamp", **kwargs):
        super().__init__(index=None, **kwargs)
        self.embedder = embedder
        self.conn = conn
        self.course = course

    def search(self, query, num_results=5):
        query_vector = self.embedder.encode(query)
        query_str = vec_to_str(query_vector)

        rows = self.conn.execute(
            """
            SELECT course, section, question, answer
            FROM documents
            WHERE course = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (self.course, query_str, num_results)
        ).fetchall()

        return [
            {"course": r[0], "section": r[1], "question": r[2], "answer": r[3]}
            for r in rows
        ]