from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_learning.filters import SearchFilters
from rag_learning.retrieval import IndexedChunk, bm25_scores, cosine_similarity, rank_chunks


class RetrievalTests(unittest.TestCase):
    def test_cosine_similarity_is_one_for_identical_vectors(self) -> None:
        score = cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        self.assertAlmostEqual(score, 1.0)

    def test_rank_chunks_applies_filters_before_sorting(self) -> None:
        chunks = [
            IndexedChunk(
                chunk_id="code-auth-1",
                text="auth text",
                source_path="data/codebase/auth_service.py",
                title="Auth",
                source_type="code",
                module="authentication",
                embedding=[1.0, 0.0],
                language="python",
            ),
            IndexedChunk(
                chunk_id="doc-payments-1",
                text="payments text",
                source_path="data/docs/retries.md",
                title="Retries",
                source_type="doc",
                module="payments",
                embedding=[0.9, 0.1],
            ),
        ]

        ranked = rank_chunks(
            [1.0, 0.0],
            chunks,
            query_text="auth text",
            top_k=3,
            filters=SearchFilters.from_cli(source_types=["code"], module="authentication"),
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0][1].chunk_id, "code-auth-1")

    def test_bm25_scores_exact_identifier_matches(self) -> None:
        chunks = [
            IndexedChunk(
                chunk_id="ticket-retry-1",
                text="Retry ticket summary for the payment gateway.",
                source_path="data/tickets/ticket-retry-logic.md",
                title="Retry Logic",
                source_type="ticket",
                module="payments",
                embedding=[1.0, 0.0],
                ticket_id="TKT-204",
            ),
            IndexedChunk(
                chunk_id="doc-notifications-1",
                text="Notification routing design notes.",
                source_path="data/docs/notifications.md",
                title="Notifications",
                source_type="doc",
                module="notifications",
                embedding=[1.0, 0.0],
            ),
        ]

        scores = bm25_scores("TKT-204", chunks)

        self.assertGreater(scores[0], 0.0)
        self.assertEqual(scores[1], 0.0)

    def test_rank_chunks_uses_bm25_to_help_exact_symbol_queries(self) -> None:
        chunks = [
            IndexedChunk(
                chunk_id="doc-retries-1",
                text="Retry logic improves resilience when the payment gateway times out.",
                source_path="data/docs/retries.md",
                title="Retries",
                source_type="doc",
                module="payments",
                embedding=[1.0, 0.0],
            ),
            IndexedChunk(
                chunk_id="code-retry-1",
                text="def retry_payment_call():\n    pass",
                source_path="data/codebase/retry_helper.py",
                title="Retry Helper",
                source_type="code",
                module="payments",
                embedding=[0.7, 0.3],
                symbol="retry_payment_call",
                language="python",
            ),
        ]

        ranked = rank_chunks(
            [1.0, 0.0],
            chunks,
            query_text="Where is retry_payment_call defined?",
            top_k=2,
            filters=SearchFilters.from_cli(module="payments"),
            vector_weight=0.7,
            bm25_weight=0.3,
        )

        self.assertEqual(ranked[0][1].chunk_id, "code-retry-1")


if __name__ == "__main__":
    unittest.main()