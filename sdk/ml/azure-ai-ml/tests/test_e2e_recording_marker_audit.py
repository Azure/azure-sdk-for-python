import ast
from pathlib import Path


LIVE_ONLY_RECORDING_REASONS = (
    "needs re-recording",
    "new common sanitizers",
    "new test proxy sanitizers",
)


def _marker_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    parts = []
    while isinstance(decorator, ast.Attribute):
        parts.append(decorator.attr)
        decorator = decorator.value
    if isinstance(decorator, ast.Name):
        parts.append(decorator.id)
    return ".".join(reversed(parts))


def _marker_reason(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Call):
        if decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
            return decorator.args[0].value
        for keyword in decorator.keywords:
            if keyword.arg == "reason" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                return keyword.value.value
    return ""


def test_e2e_recording_staleness_markers_are_removed() -> None:
    tests_root = Path(__file__).parent
    offenders = []

    for path in tests_root.glob("**/e2etests/*.py"):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if _marker_name(decorator) != "pytest.mark.live_test_only":
                    continue
                reason = _marker_reason(decorator).lower()
                if any(marker in reason for marker in LIVE_ONLY_RECORDING_REASONS):
                    offenders.append(f"{path.relative_to(tests_root)}::{node.name}")

    assert offenders == [], (
        "Playback-gating tests must not stay live-only solely because recordings need re-recording or sanitizer updates: "
        + ", ".join(offenders)
    )
