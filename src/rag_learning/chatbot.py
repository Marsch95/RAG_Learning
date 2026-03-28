from __future__ import annotations

from dataclasses import dataclass

from .citations import Citation, build_citations
from .config import Settings
from .corpus import chunk_documents, load_project_documents
from .filters import SearchFilters
from .ollama_client import OllamaClient
from .retrieval import IndexedChunk, load_index, rank_chunks, save_index


@dataclass(slots=True)
class AnswerResult:
    answer: str
    citations: list[Citation]


class RAGChatbot:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.ollama = OllamaClient(self.settings.ollama_base_url)

    def build_index(self) -> int:
        documents = load_project_documents()
        chunks = chunk_documents(
            documents,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        indexed_chunks: list[IndexedChunk] = []
        for chunk in chunks:
            embedding = self.ollama.embed(self.settings.embed_model, chunk.text)
            indexed_chunks.append(IndexedChunk.from_chunk(chunk, embedding))

        save_index(indexed_chunks)
        return len(indexed_chunks)

    def ask(
        self,
        question: str,
        *,
        filters: SearchFilters | None = None,
    ) -> AnswerResult:
        indexed_chunks = load_index()
        query_embedding = self.ollama.embed(self.settings.embed_model, question)
        ranked = rank_chunks(
            query_embedding,
            indexed_chunks,
            top_k=self.settings.top_k,
            filters=filters,
        )
        if not ranked:
            return AnswerResult(
                answer=(
                    "No indexed chunks matched the question with the current filters. "
                    "Try rebuilding the index or relaxing the filters."
                ),
                citations=[],
            )
        context = self._build_context(ranked)
        prompt = self._build_prompt(question, context, filters)
        answer = self.ollama.chat(self.settings.chat_model, prompt)
        citations = build_citations(ranked)
        return AnswerResult(answer=answer, citations=citations)

    def _build_context(self, ranked: list[tuple[float, IndexedChunk]]) -> str:
        sections: list[str] = []
        for citation, (_, chunk) in zip(build_citations(ranked), ranked):
            sections.append(
                "\n".join(
                    [
                        f"Citation: {citation.prompt_label()}",
                        f"Text: {chunk.text}",
                    ]
                )
            )
        return "\n\n".join(sections)

    def _build_prompt(
        self,
        question: str,
        context: str,
        filters: SearchFilters | None,
    ) -> str:
        filter_text = filters.describe() if filters and not filters.is_empty() else "none"
        return (
            "Use the context to answer the question. "
            "If the answer is not supported by the context, say that clearly. "
            "When you answer, mention the citations you used.\n\n"
            f"Active filters: {filter_text}\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}"
        )