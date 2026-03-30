from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_learning.filters import SearchFilters
from rag_learning.retrieval import IndexedChunk, cosine_similarity, rank_chunks


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
            top_k=3,
            filters=SearchFilters.from_cli(source_types=["code"], module="authentication"),
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0][1].chunk_id, "code-auth-1")


if __name__ == "__main__":
    unittest.main()