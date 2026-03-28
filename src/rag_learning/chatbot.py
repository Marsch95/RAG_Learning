from __future__ import annotations

from dataclasses import dataclass

from .citations import Citation, build_citations
from .config import Settings
from .corpus import chunk_documents, load_project_documents
from .db_runtime import LiveQueryResult, build_live_query_plan, run_live_query
from .filters import SearchFilters
from .ollama_client import OllamaClient
from .retrieval import IndexedChunk, load_index, rank_chunks, save_index


@dataclass(slots=True)
class AnswerResult:
    answer: str
    citations: list[Citation]
    executed_sql: str | None = None
    rows: list[dict[str, object]] | None = None
    query_name: str | None = None


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
        ranked = self._rank_question(question, filters=filters)
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

    def ask_live_database(self, question: str) -> AnswerResult:
        plan = build_live_query_plan(question)
        live_result = run_live_query(question)
        citations = self.retrieve(plan.retrieval_question, filters=plan.filters)
        answer = self._build_live_database_answer(live_result)
        return AnswerResult(
            answer=answer,
            citations=citations,
            executed_sql=live_result.sql,
            rows=live_result.rows,
            query_name=live_result.query_name,
        )

    def retrieve(
        self,
        question: str,
        *,
        filters: SearchFilters | None = None,
    ) -> list[Citation]:
        ranked = self._rank_question(question, filters=filters)
        return build_citations(ranked)

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

    def _rank_question(
        self,
        question: str,
        *,
        filters: SearchFilters | None = None,
    ) -> list[tuple[float, IndexedChunk]]:
        indexed_chunks = load_index()
        query_embedding = self.ollama.embed(self.settings.embed_model, question)
        return rank_chunks(
            query_embedding,
            indexed_chunks,
            top_k=self.settings.top_k,
            filters=filters,
        )

    def _build_live_database_answer(self, result: LiveQueryResult) -> str:
        if result.query_name == "count_failed_payment_attempts":
            count = result.rows[0]["failed_payment_attempt_count"] if result.rows else 0
            return f"There are {count} failed payment attempts in the seeded local SQLite database."

        if result.query_name == "list_failed_payment_orders":
            if not result.rows:
                return "There are no failed payment attempts in the seeded local SQLite database."
            orders = ", ".join(
                f"order {row['order_id']} (retry_count={row['retry_count']}, reason={row['failure_reason']})"
                for row in result.rows
            )
            return f"The failed payment attempts belong to {orders}."

        if result.query_name == "list_latest_failed_payment_attempts":
            if not result.rows:
                return "There are no failed payment attempts in the seeded local SQLite database."
            attempts = ", ".join(
                f"order {row['order_id']} at {row['created_at']} (retry_count={row['retry_count']}, reason={row['failure_reason']})"
                for row in result.rows
            )
            return f"The latest failed payment attempts are {attempts}."

        if result.query_name == "count_failed_notification_deliveries":
            count = result.rows[0]["failed_notification_delivery_count"] if result.rows else 0
            return f"There are {count} failed notification deliveries in the seeded local SQLite database."

        if result.query_name == "list_failed_notification_recipients":
            if not result.rows:
                return "There are no failed notification deliveries in the seeded local SQLite database."
            recipients = ", ".join(
                f"{row['recipient']} via {row['channel']} (error={row['error_message']})"
                for row in result.rows
            )
            return f"The failed notification recipients are {recipients}."

        raise ValueError(f"Unsupported live query result: {result.query_name}")