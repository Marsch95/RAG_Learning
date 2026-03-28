from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3

from .config import SQLITE_DB_FILE, SQLITE_SEED_FILE
from .filters import SearchFilters


@dataclass(slots=True)
class LiveQueryPlan:
    query_name: str
    sql: str
    filters: SearchFilters
    description: str
    retrieval_question: str


@dataclass(slots=True)
class LiveQueryResult:
    query_name: str
    sql: str
    rows: list[dict[str, object]]
    description: str


def ensure_local_database(
    db_path: Path = SQLITE_DB_FILE,
    seed_path: Path = SQLITE_SEED_FILE,
) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        return db_path

    script = seed_path.read_text(encoding="utf-8")
    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(script)
        connection.commit()
    finally:
        connection.close()
    return db_path


def reset_local_database(
    db_path: Path = SQLITE_DB_FILE,
    seed_path: Path = SQLITE_SEED_FILE,
) -> Path:
    if db_path.exists():
        db_path.unlink()
    return ensure_local_database(db_path=db_path, seed_path=seed_path)


def execute_read_only_query(
    sql: str,
    *,
    db_path: Path = SQLITE_DB_FILE,
) -> list[dict[str, object]]:
    validate_read_only_sql(sql)
    ensure_local_database(db_path=db_path)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def validate_read_only_sql(sql: str) -> None:
    normalized = sql.strip().casefold()
    if not normalized.startswith("select"):
        raise ValueError("Only read-only SELECT queries are allowed.")

    forbidden_tokens = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "attach ", "pragma ", "vacuum "]
    if any(token in normalized for token in forbidden_tokens):
        raise ValueError("Unsafe SQL detected. Only simple read-only SELECT queries are allowed.")

    if ";" in normalized.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")


def build_live_query_plan(question: str) -> LiveQueryPlan:
    normalized = question.casefold()

    if "how many" in normalized and "failed payment" in normalized:
        return LiveQueryPlan(
            query_name="count_failed_payment_attempts",
            sql=(
                "SELECT COUNT(*) AS failed_payment_attempt_count "
                "FROM payment_attempts "
                "WHERE status = 'failed'"
            ),
            filters=SearchFilters.from_cli(
                source_types=["db_note", "db_schema", "db_query"],
                module="payments",
                database_name="acme_checkout",
                table_name="payment_attempts",
                query_name="find_failed_payment_attempts",
            ),
            description="Count payment attempts that remained failed in the seeded SQLite database.",
            retrieval_question="payment_attempts table failed payment attempts find_failed_payment_attempts retry reporting schema note",
        )

    if "which order" in normalized and "failed payment" in normalized:
        return LiveQueryPlan(
            query_name="list_failed_payment_orders",
            sql=(
                "SELECT order_id, retry_count, failure_reason "
                "FROM payment_attempts "
                "WHERE status = 'failed' "
                "ORDER BY order_id ASC"
            ),
            filters=SearchFilters.from_cli(
                source_types=["db_note", "db_schema", "db_query"],
                module="payments",
                database_name="acme_checkout",
                table_name="payment_attempts",
                query_name="find_failed_payment_attempts",
            ),
            description="List the failed payment orders in the seeded SQLite database.",
            retrieval_question="payment_attempts failed payment orders find_failed_payment_attempts retry reporting schema note",
        )

    if ("latest" in normalized or "top" in normalized) and "failed payment" in normalized:
        limit = extract_limit(question, default=2)
        return LiveQueryPlan(
            query_name="list_latest_failed_payment_attempts",
            sql=(
                "SELECT order_id, retry_count, failure_reason, created_at "
                "FROM payment_attempts "
                "WHERE status = 'failed' "
                f"ORDER BY created_at DESC LIMIT {limit}"
            ),
            filters=SearchFilters.from_cli(
                source_types=["db_note", "db_schema", "db_query"],
                module="payments",
                database_name="acme_checkout",
                table_name="payment_attempts",
                query_name="find_failed_payment_attempts",
            ),
            description=f"List the latest {limit} failed payment attempts in the seeded SQLite database.",
            retrieval_question="payment_attempts latest failed payment attempts find_failed_payment_attempts retry reporting schema note",
        )

    if "how many" in normalized and "failed notification" in normalized:
        return LiveQueryPlan(
            query_name="count_failed_notification_deliveries",
            sql=(
                "SELECT COUNT(*) AS failed_notification_delivery_count "
                "FROM notification_deliveries "
                "WHERE status = 'failed'"
            ),
            filters=SearchFilters.from_cli(
                source_types=["db_note", "db_schema", "db_query"],
                module="notifications",
                database_name="acme_checkout",
                table_name="notification_deliveries",
            ),
            description="Count failed notification deliveries in the seeded SQLite database.",
            retrieval_question="notification_deliveries NotificationService failed notification deliveries schema note query",
        )

    if "which recipient" in normalized and "failed notification" in normalized:
        return LiveQueryPlan(
            query_name="list_failed_notification_recipients",
            sql=(
                "SELECT recipient, channel, error_message "
                "FROM notification_deliveries "
                "WHERE status = 'failed' "
                "ORDER BY recipient ASC"
            ),
            filters=SearchFilters.from_cli(
                source_types=["db_note", "db_schema", "db_query"],
                module="notifications",
                database_name="acme_checkout",
                table_name="notification_deliveries",
            ),
            description="List recipients with failed notification deliveries in the seeded SQLite database.",
            retrieval_question="notification_deliveries NotificationService failed notification recipients schema note query",
        )

    raise ValueError(
        "This local live database demo only supports a small set of exact-value questions. "
        "Try one of these: 'How many failed payment attempts are there?', "
        "'Which orders had failed payment attempts?', "
        "'Show the latest 2 failed payment attempts', "
        "'How many failed notifications are there?', or "
        "'Which recipients had failed notifications?'."
    )


def run_live_query(question: str, *, db_path: Path = SQLITE_DB_FILE) -> LiveQueryResult:
    plan = build_live_query_plan(question)
    rows = execute_read_only_query(plan.sql, db_path=db_path)
    return LiveQueryResult(
        query_name=plan.query_name,
        sql=plan.sql,
        rows=rows,
        description=plan.description,
    )


def extract_limit(question: str, *, default: int) -> int:
    match = re.search(r"\b(\d+)\b", question)
    if not match:
        return default
    return max(1, min(int(match.group(1)), 10))