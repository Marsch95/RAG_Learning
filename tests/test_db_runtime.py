from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag_learning.db_runtime import build_live_query_plan, extract_limit, validate_read_only_sql


class DatabaseRuntimeTests(unittest.TestCase):
    def test_build_live_query_plan_for_latest_failed_payments(self) -> None:
        plan = build_live_query_plan("Show the latest 2 failed payment attempts.")

        self.assertEqual(plan.query_name, "list_latest_failed_payment_attempts")
        self.assertIn("LIMIT 2", plan.sql)
        self.assertEqual(plan.filters.table_name, "payment_attempts")

    def test_extract_limit_bounds_large_values(self) -> None:
        self.assertEqual(extract_limit("Show the latest 99 failed payment attempts.", default=2), 10)

    def test_validate_read_only_sql_rejects_mutation(self) -> None:
        with self.assertRaises(ValueError):
            validate_read_only_sql("DELETE FROM payment_attempts")


if __name__ == "__main__":
    unittest.main()