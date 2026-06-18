"""
DESCRIPTION:
    Terminal UI wrapper around the orchestrator. 
    
"""

import builtins
import re

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

_real_print = builtins.print
_real_input = builtins.input

console = Console(
    theme=Theme(
        {
            "tool": "cyan",
            "mcp": "magenta",
            "web": "yellow",
            "reasoning": "italic grey62",
            "system": "grey62",
            "agent": "bold green",
            "error": "bold red",
            "prompt": "bold cyan",
            "label": "dim",
        }
    )
)


_TRACE_PATTERNS: list[tuple[re.Pattern, str | None, str]] = [
    (re.compile(r"^\s*\[stage\]\s*(.*)", re.DOTALL), "label", "── {0} ──"),
    (re.compile(r"^\s*\[reasoning\]\s*(.*)", re.DOTALL), "reasoning", "·  reasoning"),
    (re.compile(r"^\s*\[text\]\s*(.*)", re.DOTALL), None, ""),
    (re.compile(r"^\s*\[tool\]\s*(.*)", re.DOTALL), "tool", "→  tool"),
    (re.compile(r"^\s*\[tool-result\]\s*(.*)", re.DOTALL), "tool", "←  result"),
    (re.compile(r"^\s*\[mcp_list_tools\]\s*(.*)", re.DOTALL), "mcp", "·  mcp"),
    (re.compile(r"^\s*\[mcp\]\s*(.*)", re.DOTALL), "mcp", "→  mcp"),
    (re.compile(r"^\s*\[web\]\s*(.*)", re.DOTALL), "web", "→  web"),
    (re.compile(r"^\s*\[oauth_consent_request\].*", re.DOTALL), "error", "!  oauth required"),
    (re.compile(r"^\s*\[empty-response\]\s*$"), "error", "!  empty response (no output items)"),
    (re.compile(r"^\s*\[message\]\s*(.*)", re.DOTALL), "error", "!  message"),
    (re.compile(r"^\s*\[([a-z_]+)\]\s*$"), "label", "·  {0}"),
]


def _format_trace(msg: str) -> bool:
    """If ``msg`` is a trace line emitted by orchestrator.trace(), render it. Returns True if handled."""
    for pattern, style, label in _TRACE_PATTERNS:
        m = pattern.match(msg)
        if not m:
            continue
        if style is None:
            return True  # suppressed (e.g. [text] is replayed in the final answer)
        payload = m.group(1).strip() if m.groups() else ""
        rendered_label = label.format(payload) if "{0}" in label else label
        line = f"  [{style}]{rendered_label}[/]"
        if payload and "{0}" not in label:
            line += f"  [label]{payload}[/]"
        console.print(line, highlight=False)
        return True
    return False


def _ui_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    msg = sep.join(str(a) for a in args)
    stripped = msg.strip()

    if not stripped:
        _real_print()
        return

    if _format_trace(msg):
        return

    if stripped.startswith("agent>"):
        body = stripped[len("agent>"):].strip()
        if body.startswith("[") and body.endswith("]"):
            console.print(Panel(body, title="agent", border_style="error", padding=(0, 1)))
        else:
            console.print(
                Panel(Markdown(body), title="agent", border_style="agent", padding=(1, 2))
            )
        return

    if stripped.startswith(("Onboarding sub-agent:", "Agent:", "Deleted ")):
        console.print(f"[system]{stripped}[/]", highlight=False)
        return

    if stripped.startswith("Cleanup failed"):
        console.print(f"[error]{stripped}[/]", highlight=False)
        return

    if stripped.startswith("Type a message"):
        console.rule("[bold cyan]SDK Dev Agent[/]")
        console.print(f"[system]{stripped}[/]\n", highlight=False)
        return

    console.print(stripped, highlight=False)


def _ui_input(prompt: str = "") -> str:
    label = prompt.rstrip().rstrip(">").strip() or "you"
    console.print(f"[prompt]{label}›[/] ", end="")
    return _real_input("")


def main() -> None:
    builtins.print = _ui_print
    builtins.input = _ui_input
    try:
        from .agents import orchestrator  # noqa: F401  (import-time side effects run the loop)
    except KeyboardInterrupt:
        console.print("\n[system]interrupted[/]")
    finally:
        builtins.print = _real_print
        builtins.input = _real_input


if __name__ == "__main__":
    main()
