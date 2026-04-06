import time

from langgraph.graph import StateGraph, START, END

from app.core.embedder import Embedder
from app.core.generator import Generator
from app.repositories.base import ChunkRepository
from app.pipelines.state import QueryState


SCORE_THRESHOLD = 0.5


class QueryPipeline:
    def __init__(
        self,
        embedder: Embedder,
        chunk_repository: ChunkRepository,
        generator: Generator,
    ):
        self.embedder = embedder
        self.chunk_repository = chunk_repository
        self.generator = generator
        self.graph = self._build_graph()

    def run(self, query: str, top_k: int, filters: dict, debug: bool) -> QueryState:
        initial_state: QueryState = {
            "query": query,
            "top_k": top_k,
            "filters": filters,
            "debug": debug,
            "query_embedding": None,
            "retrieved_chunks": [],
            "ranked_chunks": [],
            "answer": None,
            "timings": {},
        }
        return self.graph.invoke(initial_state)

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(QueryState)

        graph.add_node("embed", self._embed)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("rank", self._rank)
        graph.add_node("generate", self._generate)

        graph.add_edge(START, "embed")
        graph.add_edge("embed", "retrieve")
        graph.add_edge("retrieve", "rank")
        graph.add_edge("rank", "generate")
        graph.add_edge("generate", END)

        return graph.compile()

    def _embed(self, state: QueryState) -> dict:
        start = time.monotonic()
        embedding = self.embedder.embed(state["query"])
        elapsed_ms = round((time.monotonic() - start) * 1000)

        return {
            "query_embedding": embedding,
            "timings": {**state["timings"], "embedding_ms": elapsed_ms},
        }

    def _retrieve(self, state: QueryState) -> dict:
        start = time.monotonic()
        chunks = self.chunk_repository.search(
            embedding=state["query_embedding"],
            top_k=state["top_k"],
        )
        elapsed_ms = round((time.monotonic() - start) * 1000)

        return {
            "retrieved_chunks": chunks,
            "timings": {**state["timings"], "retrieval_ms": elapsed_ms},
        }

    def _rank(self, state: QueryState) -> dict:
        ranked = [c for c in state["retrieved_chunks"] if c.score >= SCORE_THRESHOLD]

        # Fallback: if nothing clears the threshold, keep the top result
        # so generation always has at least some context.
        if not ranked and state["retrieved_chunks"]:
            ranked = [state["retrieved_chunks"][0]]

        return {"ranked_chunks": ranked}

    def _generate(self, state: QueryState) -> dict:
        context = "\n\n".join(
            f"[{c.document_name}]\n{c.content}" for c in state["ranked_chunks"]
        )

        start = time.monotonic()
        answer = self.generator.generate(query=state["query"], context=context)
        elapsed_ms = round((time.monotonic() - start) * 1000)

        return {
            "answer": answer,
            "timings": {**state["timings"], "generation_ms": elapsed_ms},
        }
