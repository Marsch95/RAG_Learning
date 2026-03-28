from __future__ import annotations

import argparse

from .chatbot import RAGChatbot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local RAG learning project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("index", help="Build the local document index")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the local index")
    ask_parser.add_argument("question", help="Question to ask the chatbot")
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
        result = chatbot.ask(args.question)
        print("Answer:\n")
        print(result.answer)
        print("\nCitations:")
        for citation in result.citations:
            print(f"- {citation}")
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()