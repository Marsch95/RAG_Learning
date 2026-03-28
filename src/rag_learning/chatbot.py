from __future__ import annotations

from dataclasses import dataclass

from .config import DOCS_DIR, Settings
from .corpus import chunk_documents, load_markdown_documents
from .ollama_client import OllamaClient
from .retrieval import IndexedChunk, load_index, rank_chunks, save_index


@dataclass(slots=True)
class AnswerResult:
    answer: str
    citations: list[str]


class RAGChatbot:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.ollama = OllamaClient(self.settings.ollama_base_url)

    def build_index(self) -> int:
        documents = load_markdown_documents(DOCS_DIR)
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

    def ask(self, question: str) -> AnswerResult:
        indexed_chunks = load_index()
        query_embedding = self.ollama.embed(self.settings.embed_model, question)
        ranked = rank_chunks(query_embedding, indexed_chunks, top_k=self.settings.top_k)
        context = self._build_context(ranked)
        prompt = self._build_prompt(question, context)
        answer = self.ollama.chat(self.settings.chat_model, prompt)
        citations = [self._citation_text(chunk) for _, chunk in ranked]
        return AnswerResult(answer=answer, citations=citations)

    def _build_context(self, ranked: list[tuple[float, IndexedChunk]]) -> str:
        sections: list[str] = []
        for score, chunk in ranked:
            sections.append(
                "\n".join(
                    [
                        f"Citation: {self._citation_text(chunk)}",
                        f"Similarity: {score:.3f}",
                        f"Text: {chunk.text}",
                    ]
                )
            )
        return "\n\n".join(sections)

    def _build_prompt(self, question: str, context: str) -> str:
        return (
            "Use the context to answer the question. "
            "If the answer is not supported by the context, say that clearly. "
            "When you answer, mention the citations you used.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}"
        )

    def _citation_text(self, chunk: IndexedChunk) -> str:
        return f"{chunk.chunk_id} ({chunk.source_path})"