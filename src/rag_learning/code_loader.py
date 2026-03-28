from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CodeDocument:
    text: str
    source_path: str
    title: str
    module: str
    symbol: str | None = None
    ticket_id: str | None = None
    updated_at: str | None = None
    language: str = "python"
    source_type: str = "code"
    database_name: str | None = None
    table_name: str | None = None
    query_name: str | None = None
    service_name: str | None = None


CODE_FILE_METADATA: dict[str, dict[str, str]] = {
    "auth_service": {
        "module": "authentication",
        "updated_at": "2026-03-05",
    },
    "notifications": {
        "module": "notifications",
        "ticket_id": "TKT-207",
        "updated_at": "2026-03-14",
    },
    "payment_gateway": {
        "module": "payments",
        "ticket_id": "TKT-204",
        "updated_at": "2026-03-10",
    },
    "retry_helper": {
        "module": "payments",
        "ticket_id": "TKT-204",
        "updated_at": "2026-03-12",
    },
    "notification_repository": {
        "module": "notifications",
        "ticket_id": "TKT-207",
        "updated_at": "2026-03-17",
        "database_name": "acme_checkout",
        "table_name": "notification_deliveries",
        "service_name": "NotificationService",
    },
}


def load_code_documents(code_dir: Path, project_root: Path) -> list[CodeDocument]:
    documents: list[CodeDocument] = []
    for path in sorted(code_dir.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        metadata = code_metadata_for_path(path)
        source_path = str(path.relative_to(project_root))

        documents.append(
            CodeDocument(
                text=build_module_document(source, tree, path.stem),
                source_path=source_path,
                title=f"Code Overview: {path.stem}",
                module=metadata["module"],
                ticket_id=metadata.get("ticket_id"),
                updated_at=metadata.get("updated_at"),
                database_name=metadata.get("database_name"),
                table_name=metadata.get("table_name"),
                service_name=metadata.get("service_name"),
            )
        )

        for node in top_level_code_nodes(tree):
            symbol_name = node.name
            symbol_type = "class" if isinstance(node, ast.ClassDef) else "function"
            symbol_source = ast.get_source_segment(source, node) or extract_source_by_lines(source, node)
            documents.append(
                CodeDocument(
                    text=build_symbol_document(path.stem, symbol_name, symbol_type, symbol_source),
                    source_path=source_path,
                    title=f"Code Symbol: {symbol_name}",
                    module=metadata["module"],
                    symbol=symbol_name,
                    ticket_id=metadata.get("ticket_id"),
                    updated_at=metadata.get("updated_at"),
                    database_name=metadata.get("database_name"),
                    table_name=metadata.get("table_name"),
                    service_name=metadata.get("service_name"),
                )
            )

    return documents


def build_module_document(source: str, tree: ast.Module, file_stem: str) -> str:
    module_docstring = ast.get_docstring(tree) or "No module docstring provided."
    symbol_names = [node.name for node in top_level_code_nodes(tree)]
    symbols_text = ", ".join(symbol_names) if symbol_names else "none"
    return "\n".join(
        [
            f"Module file: {file_stem}.py",
            f"Module summary: {module_docstring}",
            f"Top-level symbols: {symbols_text}",
            "Code:",
            source.strip(),
        ]
    )


def build_symbol_document(
    file_stem: str,
    symbol_name: str,
    symbol_type: str,
    symbol_source: str,
) -> str:
    return "\n".join(
        [
            f"Module file: {file_stem}.py",
            f"Symbol name: {symbol_name}",
            f"Symbol type: {symbol_type}",
            "Code:",
            symbol_source.strip(),
        ]
    )


def top_level_code_nodes(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef]:
    allowed_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    return [node for node in tree.body if isinstance(node, allowed_types)]


def extract_source_by_lines(
    source: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> str:
    lines = source.splitlines()
    start_line = node.lineno - 1
    end_line = getattr(node, "end_lineno", node.lineno)
    return "\n".join(lines[start_line:end_line])


def code_metadata_for_path(path: Path) -> dict[str, str]:
    return CODE_FILE_METADATA.get(
        path.stem,
        {
            "module": path.stem.replace("_", "-"),
            "updated_at": "2026-03-01",
        },
    )
