from pathlib import Path
from typing import Any, Callable

from azure.ai.projects.models import FunctionTool


def find_repo() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").is_file() and (parent / "sdk").is_dir():
            return parent
    raise RuntimeError("Could not locate azure-sdk-for-python repo root.")


repo_root = find_repo()
_max_bytes = 64 * 1024


def read_repo(path: str, start_line: int = 1, end_line: int | None = None) -> dict[str, Any]:
    target = (repo_root / path).resolve()
    if repo_root not in target.parents and target != repo_root:
        return {"error": f"path escapes repo root: {path}"}
    if not target.is_file():
        return {"error": f"not a file: {path}"}

    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = max(1, start_line)
    end = end_line if end_line is not None else len(lines)
    end = min(end, len(lines))
    snippet = "\n".join(lines[start - 1 : end])
    if len(snippet.encode("utf-8")) > _max_bytes:
        snippet = snippet.encode("utf-8")[:_max_bytes].decode("utf-8", errors="ignore")
        snippet += "\n... (truncated)"
    return {
        "path": str(target.relative_to(repo_root)).replace("\\", "/"),
        "start_line": start,
        "end_line": end,
        "total_lines": len(lines),
        "content": snippet,
    }


tools: list[FunctionTool] = [
    FunctionTool(
        name="read_repo",
        description=(
            "Read a slice of a text file from the azure-sdk-for-python repo. "
            "Path is repo-root-relative (use forward slashes). Returns the "
            "requested line range plus metadata."
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Repo-relative path, e.g. 'sdk/ai/azure-ai-projects/README.md'.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "1-based first line to read. Default 1.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "1-based last line to read (inclusive). Default end of file.",
                },
            },
            "required": ["path", "start_line", "end_line"],
            "additionalProperties": False,
        },
        strict=True,
    ),
]


functions: dict[str, Callable[..., Any]] = {
    "read_repo": read_repo,
}
