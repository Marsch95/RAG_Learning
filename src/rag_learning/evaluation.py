from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

from .chatbot import RAGChatbot
from .citations import Citation
from .config import EVAL_QUESTIONS_FILE, EVAL_REPORT_FILE, ensure_eval_dir
from .filters import SearchFilters, clean_text, normalize_source_types, normalize_text, normalize_ticket_id


@dataclass(slots=True)
class EvaluationCase:
    case_id: str
    question: str
    answer_mode: str = "retrieval"
    filters: SearchFilters = field(default_factory=SearchFilters)
    expected_source_types: tuple[str, ...] = field(default_factory=tuple)
    expected_module: str | None = None
    expected_ticket_id: str | None = None
    expected_change_id: str | None = None
    expected_symbol: str | None = None
    expected_database_name: str | None = None
    expected_table_name: str | None = None
    expected_query_name: str | None = None
    expected_service_name: str | None = None
    expected_paths: tuple[str, ...] = field(default_factory=tuple)
    reference_points: tuple[str, ...] = field(default_factory=tuple)
    expected_answer_contains: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, payload: dict) -> "EvaluationCase":
        filter_payload = payload.get("filters", {})
        return cls(
            case_id=payload["case_id"],
            question=payload["question"],
            answer_mode=payload.get("answer_mode", "retrieval"),
            filters=SearchFilters.from_cli(
                source_types=filter_payload.get("source_types")
                or source_type_to_list(filter_payload.get("source_type")),
                module=filter_payload.get("module"),
                ticket_id=filter_payload.get("ticket_id"),
                change_id=filter_payload.get("change_id"),
                symbol=filter_payload.get("symbol"),
                language=filter_payload.get("language"),
                database_name=filter_payload.get("database_name"),
                table_name=filter_payload.get("table_name"),
                query_name=filter_payload.get("query_name"),
                service_name=filter_payload.get("service_name"),
                updated_after=filter_payload.get("updated_after"),
            ),
            expected_source_types=normalize_source_types(payload.get("expected_source_types")),
            expected_module=clean_text(payload.get("expected_module")),
            expected_ticket_id=normalize_ticket_id(payload.get("expected_ticket_id")),
            expected_change_id=clean_text(payload.get("expected_change_id")),
            expected_symbol=clean_text(payload.get("expected_symbol")),
            expected_database_name=clean_text(payload.get("expected_database_name")),
            expected_table_name=clean_text(payload.get("expected_table_name")),
            expected_query_name=clean_text(payload.get("expected_query_name")),
            expected_service_name=clean_text(payload.get("expected_service_name")),
            expected_paths=tuple(payload.get("expected_paths", [])),
            reference_points=tuple(payload.get("reference_points", [])),
            expected_answer_contains=tuple(payload.get("expected_answer_contains", [])),
        )


@dataclass(slots=True)
class EvaluationCaseResult:
    case_id: str
    question: str
    filters: dict[str, object]
    retrieval_metrics: dict[str, bool]
    top_citation: dict[str, object] | None
    citations: list[dict[str, object]]
    reference_points: list[str]
    answer: str | None = None
    review_template: dict[str, object] | None = None
    answer_metrics: dict[str, bool] | None = None


@dataclass(slots=True)
class EvaluationReport:
    question_count: int
    include_answers: bool
    summary: dict[str, float | int]
    results: list[EvaluationCaseResult]

    def to_dict(self) -> dict[str, object]:
        return {
            "question_count": self.question_count,
            "include_answers": self.include_answers,
            "summary": self.summary,
            "results": [asdict(result) for result in self.results],
        }


def load_evaluation_cases(path: Path = EVAL_QUESTIONS_FILE) -> list[EvaluationCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Evaluation questions file must contain a JSON list.")
    return [EvaluationCase.from_dict(item) for item in payload]


def evaluate_questions(
    chatbot: RAGChatbot,
    *,
    questions_path: Path = EVAL_QUESTIONS_FILE,
    include_answers: bool = False,
    output_path: Path = EVAL_REPORT_FILE,
) -> EvaluationReport:
    cases = load_evaluation_cases(questions_path)
    results: list[EvaluationCaseResult] = []

    for case in cases:
        if case.answer_mode == "live_db":
            live_result = chatbot.ask_live_database(case.question)
            citations = live_result.citations
            answer = live_result.answer
        else:
            citations = chatbot.retrieve(case.question, filters=case.filters)
            answer = None

        retrieval_metrics = score_retrieval(case, citations)
        review_template = None
        answer_metrics = None

        if case.answer_mode == "live_db":
            answer_metrics = score_answer(case, answer or "")
            retrieval_metrics["overall_hit"] = retrieval_metrics["overall_hit"] and answer_metrics["answer_contains_hit"]
            review_template = {
                "grounded_in_retrieved_evidence": "",
                "matches_live_query_result": "",
                "notes": "",
            }
        elif include_answers:
            answer = chatbot.ask(case.question, filters=case.filters).answer
            review_template = {
                "grounded_in_retrieved_evidence": "",
                "mentions_key_reference_points": "",
                "answer_quality": "",
                "notes": "",
            }

        results.append(
            EvaluationCaseResult(
                case_id=case.case_id,
                question=case.question,
                filters=filters_to_dict(case.filters),
                retrieval_metrics=retrieval_metrics,
                top_citation=citation_to_dict(citations[0]) if citations else None,
                citations=[citation_to_dict(citation) for citation in citations],
                reference_points=list(case.reference_points),
                answer=answer,
                review_template=review_template,
                answer_metrics=answer_metrics,
            )
        )

    report = EvaluationReport(
        question_count=len(results),
        include_answers=include_answers,
        summary=build_summary(results),
        results=results,
    )
    save_report(report, output_path)
    return report


def save_report(report: EvaluationReport, output_path: Path = EVAL_REPORT_FILE) -> None:
    ensure_eval_dir()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def build_summary(results: list[EvaluationCaseResult]) -> dict[str, float | int]:
    question_count = len(results)
    if question_count == 0:
        return {"question_count": 0}

    metric_names = [
        "source_type_hit",
        "module_hit",
        "ticket_hit",
        "change_hit",
        "symbol_hit",
        "database_hit",
        "table_hit",
        "query_hit",
        "service_hit",
        "path_hit",
        "answer_contains_hit",
        "overall_hit",
    ]

    summary: dict[str, float | int] = {"question_count": question_count}
    for metric_name in metric_names:
        applicable_count = question_count
        if metric_name == "answer_contains_hit":
            applicable_count = sum(1 for result in results if result.answer_metrics is not None)

        hits = sum(
            1
            for result in results
            if result.retrieval_metrics.get(metric_name, False)
            or (result.answer_metrics and result.answer_metrics.get(metric_name, False))
        )
        summary[f"{metric_name}_count"] = hits
        summary[f"{metric_name}_rate"] = round(hits / applicable_count, 3) if applicable_count else 0.0
        if metric_name == "answer_contains_hit":
            summary["answer_contains_hit_applicable_count"] = applicable_count
    return summary


def score_retrieval(case: EvaluationCase, citations: list[Citation]) -> dict[str, bool]:
    source_type_hit = all(
        any(citation.source_type == expected_source_type for citation in citations)
        for expected_source_type in case.expected_source_types
    ) if case.expected_source_types else True

    module_hit = any(
        normalize_text(citation.module) == normalize_text(case.expected_module)
        for citation in citations
    ) if case.expected_module else True

    database_hit = any(
        normalize_text(citation.database_name) == normalize_text(case.expected_database_name)
        for citation in citations
    ) if case.expected_database_name else True

    table_hit = any(
        normalize_text(citation.table_name) == normalize_text(case.expected_table_name)
        for citation in citations
    ) if case.expected_table_name else True

    query_hit = any(
        normalize_text(citation.query_name) == normalize_text(case.expected_query_name)
        for citation in citations
    ) if case.expected_query_name else True

    service_hit = any(
        normalize_text(citation.service_name) == normalize_text(case.expected_service_name)
        for citation in citations
    ) if case.expected_service_name else True

    ticket_hit = any(
        normalize_ticket_id(citation.ticket_id) == normalize_ticket_id(case.expected_ticket_id)
        for citation in citations
    ) if case.expected_ticket_id else True

    change_hit = any(
        normalize_text(citation.change_id) == normalize_text(case.expected_change_id)
        for citation in citations
    ) if case.expected_change_id else True

    symbol_hit = any(
        citation.symbol is not None
        and normalize_text(case.expected_symbol) in normalize_text(citation.symbol)
        for citation in citations
    ) if case.expected_symbol else True

    normalized_expected_paths = {normalize_path(path) for path in case.expected_paths}
    path_hit = any(normalize_path(citation.source_path) in normalized_expected_paths for citation in citations) if case.expected_paths else True

    overall_checks = [
        source_type_hit,
        module_hit,
        ticket_hit,
        change_hit,
        symbol_hit,
        database_hit,
        table_hit,
        query_hit,
        service_hit,
        path_hit,
    ]
    return {
        "source_type_hit": source_type_hit,
        "module_hit": module_hit,
        "ticket_hit": ticket_hit,
        "change_hit": change_hit,
        "symbol_hit": symbol_hit,
        "database_hit": database_hit,
        "table_hit": table_hit,
        "query_hit": query_hit,
        "service_hit": service_hit,
        "path_hit": path_hit,
        "overall_hit": all(overall_checks),
    }


def score_answer(case: EvaluationCase, answer: str) -> dict[str, bool]:
    normalized_answer = answer.casefold()
    answer_contains_hit = all(expected.casefold() in normalized_answer for expected in case.expected_answer_contains)
    return {"answer_contains_hit": answer_contains_hit}


def citation_to_dict(citation: Citation) -> dict[str, object]:
    return {
        "chunk_id": citation.chunk_id,
        "title": citation.title,
        "source_path": citation.source_path,
        "source_type": citation.source_type,
        "module": citation.module,
        "score": round(citation.score, 3),
        "ticket_id": citation.ticket_id,
        "change_id": citation.change_id,
        "updated_at": citation.updated_at,
        "symbol": citation.symbol,
        "language": citation.language,
        "database_name": citation.database_name,
        "table_name": citation.table_name,
        "query_name": citation.query_name,
        "service_name": citation.service_name,
    }


def filters_to_dict(filters: SearchFilters) -> dict[str, object]:
    return {
        "source_types": list(filters.source_types),
        "module": filters.module,
        "ticket_id": filters.ticket_id,
        "change_id": filters.change_id,
        "symbol": filters.symbol,
        "language": filters.language,
        "database_name": filters.database_name,
        "table_name": filters.table_name,
        "query_name": filters.query_name,
        "service_name": filters.service_name,
        "updated_after": filters.updated_after,
    }


def source_type_to_list(source_type: str | None) -> list[str] | None:
    cleaned = clean_text(source_type)
    if cleaned is None:
        return None
    return [cleaned]


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def summary_lines(report: EvaluationReport) -> list[str]:
    summary = report.summary
    return [
        f"Questions evaluated: {summary['question_count']}",
        f"Overall retrieval hit rate: {summary['overall_hit_count']}/{summary['question_count']} ({summary['overall_hit_rate']:.1%})",
        f"Source type hit rate: {summary['source_type_hit_count']}/{summary['question_count']} ({summary['source_type_hit_rate']:.1%})",
        f"Module hit rate: {summary['module_hit_count']}/{summary['question_count']} ({summary['module_hit_rate']:.1%})",
        f"Table hit rate: {summary['table_hit_count']}/{summary['question_count']} ({summary['table_hit_rate']:.1%})",
        f"Path hit rate: {summary['path_hit_count']}/{summary['question_count']} ({summary['path_hit_rate']:.1%})",
        f"Answer content hit rate: {summary['answer_contains_hit_count']}/{summary['answer_contains_hit_applicable_count']} ({summary['answer_contains_hit_rate']:.1%})",
    ]