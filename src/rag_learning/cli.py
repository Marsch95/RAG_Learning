from __future__ import annotations

import argparse
from pathlib import Path

from .chatbot import RAGChatbot
from .citations import group_citations
from .config import EVAL_QUESTIONS_FILE, EVAL_REPORT_FILE
from .evaluation import evaluate_questions, summary_lines
from .filters import SearchFilters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local RAG learning project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("index", help="Build the local document index")

    evaluate_parser = subparsers.add_parser("evaluate", help="Run the Phase 5 evaluation set")
    evaluate_parser.add_argument(
        "--questions-file",
        default=str(EVAL_QUESTIONS_FILE),
        help="Path to the JSON evaluation dataset",
    )
    evaluate_parser.add_argument(
        "--output",
        default=str(EVAL_REPORT_FILE),
        help="Path to write the JSON evaluation report",
    )
    evaluate_parser.add_argument(
        "--with-answers",
        action="store_true",
        help="Also generate answers so the report can be used for manual answer review",
    )

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the local index")
    ask_parser.add_argument("question", help="Question to ask the chatbot")
    ask_parser.add_argument(
        "--source-type",
        action="append",
        choices=["doc", "ticket", "change", "code", "db_note", "db_schema", "db_query"],
        help="Limit retrieval to one or more source types. Repeat the flag to combine values.",
    )
    ask_parser.add_argument(
        "--module",
        help="Limit retrieval to one module such as authentication, notifications, payments, or platform",
    )
    ask_parser.add_argument(
        "--ticket-id",
        help="Limit retrieval to one fake ticket such as TKT-204",
    )
    ask_parser.add_argument(
        "--change-id",
        help="Limit retrieval to one fake change note such as CHG-204",
    )
    ask_parser.add_argument(
        "--symbol",
        help="Limit retrieval to code symbols whose name contains this text",
    )
    ask_parser.add_argument(
        "--language",
        help="Limit retrieval to one language such as python",
    )
    ask_parser.add_argument(
        "--database-name",
        help="Limit retrieval to one database such as acme_checkout",
    )
    ask_parser.add_argument(
        "--table-name",
        help="Limit retrieval to one database table such as notification_deliveries",
    )
    ask_parser.add_argument(
        "--query-name",
        help="Limit retrieval to one query such as find_failed_payment_attempts",
    )
    ask_parser.add_argument(
        "--service-name",
        help="Limit retrieval to one service such as NotificationService",
    )
    ask_parser.add_argument(
        "--updated-after",
        help="Only include chunks updated on or after an ISO date such as 2026-03-10",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    chatbot = RAGChatbot()

    if args.command == "index":
        chunk_count = chatbot.build_index()
        print(f"Indexed {chunk_count} chunks into the local JSON index.")
        return

    if args.command == "ask":
        filters = SearchFilters.from_cli(
            source_types=args.source_type,
            module=args.module,
            ticket_id=args.ticket_id,
            change_id=args.change_id,
            symbol=args.symbol,
            language=args.language,
            database_name=args.database_name,
            table_name=args.table_name,
            query_name=args.query_name,
            service_name=args.service_name,
            updated_after=args.updated_after,
        )
        result = chatbot.ask(args.question, filters=filters)
        if not filters.is_empty():
            print("Filters:\n")
            print(filters.describe())
            print()
        print("Answer:\n")
        print(result.answer)
        print("\nEvidence:")
        for group in group_citations(result.citations):
            print(f"\n{group.heading}:")
            for citation in group.citations:
                print(f"- {citation.display_line()}")
        return

    if args.command == "evaluate":
        report = evaluate_questions(
            chatbot,
            questions_path=Path(args.questions_file),
            include_answers=args.with_answers,
            output_path=Path(args.output),
        )
        print("Evaluation Summary:\n")
        for line in summary_lines(report):
            print(line)
        print(f"\nDetailed report written to {args.output}")
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()