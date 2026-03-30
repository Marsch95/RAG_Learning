from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_learning.filters import SearchFilters, matches_filters, normalize_source_types


class DummyItem:
    source_type = "code"
    module = "payments"
    ticket_id = "TKT-204"
    change_id = "CHG-001"
    symbol = "retry_payment_call"
    language = "python"
    database_name = "acme_checkout"
    table_name = "payment_attempts"
    query_name = "find_failed_payment_attempts"
    service_name = "PaymentReportingQuery"
    updated_at = "2026-03-12"


class SearchFiltersTests(unittest.TestCase):
    def test_from_cli_normalizes_values(self) -> None:
        filters = SearchFilters.from_cli(
            source_types=["CODE", "code", "db_query"],
            module=" payments ",
            ticket_id="tkt-204",
            language="Python",
        )

        self.assertEqual(filters.source_types, ("code", "db_query"))
        self.assertEqual(filters.module, "payments")
        self.assertEqual(filters.ticket_id, "TKT-204")
        self.assertEqual(filters.language, "python")

    def test_matches_filters_accepts_matching_item(self) -> None:
        filters = SearchFilters.from_cli(
            source_types=["code"],
            module="payments",
            ticket_id="TKT-204",
            symbol="retry_payment",
            language="python",
        )

        self.assertTrue(matches_filters(DummyItem(), filters))

    def test_matches_filters_rejects_wrong_table(self) -> None:
        filters = SearchFilters.from_cli(table_name="notification_deliveries")
        self.assertFalse(matches_filters(DummyItem(), filters))

    def test_normalize_source_types_deduplicates(self) -> None:
        self.assertEqual(normalize_source_types(["doc", "DOC", "ticket"]), ("doc", "ticket"))


if __name__ == "__main__":
    unittest.main()