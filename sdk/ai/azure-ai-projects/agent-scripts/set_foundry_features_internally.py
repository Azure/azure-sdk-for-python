#!/usr/bin/env python3
"""Apply foundry preview feature opt-in changes to generated operations files.

This script is intended to be run from:
  sdk/ai/azure-ai-projects

It only edits the following files:
- azure/ai/projects/aio/operations/_operations.py
- azure/ai/projects/operations/_operations.py
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

TARGET_FILES = [
    Path("azure/ai/projects/aio/operations/_operations.py"),
    Path("azure/ai/projects/operations/_operations.py"),
]

INSERT_LINE = (
    "_get_foundry_features_opt_in_keys: str = \",\".join([key.value for key in "
    "_models.AgentDefinitionOptInKeys] + [key.value for key in _models.FoundryFeaturesOptInKeys])"
)

RE_DEF = re.compile(r"^(?P<indent>\s*)(?:async\s+def|def)\s+(?P<name>\w+)\s*\(")
RE_FOUNDRY_ASSIGN = re.compile(r"foundry_features\s*=\s*foundry_features,")
RE_SIGNATURE = re.compile(
    r"(?P<head>^[ \t]*(?:async\s+def|def)\s+(?P<name>\w+)\s*\()"
    r"(?P<params>[\s\S]*?)"
    r"(?P<tail>\)[ \t]*(?:->[\s\S]*?)?:)",
    re.MULTILINE,
)


def split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    paren = 0
    bracket = 0
    brace = 0

    for i, ch in enumerate(text):
        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
        elif ch == "," and paren == 0 and bracket == 0 and brace == 0:
            parts.append(text[start:i])
            start = i + 1

    parts.append(text[start:])
    return parts


def find_matching_paren(text: str, open_index: int) -> int:
    depth = 0
    for i in range(open_index, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def remove_foundry_param_from_signature(signature: str) -> tuple[str, bool]:
    if "foundry_features:" not in signature:
        return signature, False

    open_index = signature.find("(")
    if open_index == -1:
        return signature, False

    close_index = find_matching_paren(signature, open_index)
    if close_index == -1:
        return signature, False

    head = signature[: open_index + 1]
    params = signature[open_index + 1 : close_index]
    tail = signature[close_index:]

    parts = split_top_level_commas(params)
    kept_parts = [p for p in parts if "foundry_features:" not in p]

    if len(kept_parts) == len(parts):
        return signature, False

    # Remove keyword-only marker '*' if it only prefixes **kwargs after removal.
    star_indexes = [idx for idx, part in enumerate(kept_parts) if part.strip() == "*"]
    for idx in reversed(star_indexes):
        has_non_kwargs_after = any(
            p.strip() and not p.strip().startswith("**") for p in kept_parts[idx + 1 :]
        )
        if not has_non_kwargs_after:
            kept_parts.pop(idx)

    new_params = ",".join(kept_parts)
    return f"{head}{new_params}{tail}", True


def strip_foundry_docstring_sections(text: str) -> str:
    text = re.sub(r"^[ \t]*:paramtype foundry_features:.*\n", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"^[ \t]*:keyword foundry_features:.*\n(?:^[ \t]+(?!:).*(?:\n|$))*",
        "",
        text,
        flags=re.MULTILINE,
    )
    return text


def strip_foundry_from_signatures(text: str) -> tuple[str, bool]:
    changed = False
    pieces: list[str] = []
    last = 0

    for match in RE_SIGNATURE.finditer(text):
        pieces.append(text[last : match.start()])

        name = match.group("name")
        signature = match.group(0)

        if name.startswith("build_") or "foundry_features:" not in signature:
            pieces.append(signature)
        else:
            new_signature, sig_changed = remove_foundry_param_from_signature(signature)
            if sig_changed:
                changed = True
            pieces.append(new_signature)

        last = match.end()

    pieces.append(text[last:])
    return "".join(pieces), changed


def insert_opt_in_constant(lines: list[str]) -> tuple[list[str], bool]:
    if any(line.strip() == INSERT_LINE for line in lines):
        return lines, False

    for i, line in enumerate(lines):
        if line.startswith("JSON = MutableMapping"):
            return lines[:i] + [INSERT_LINE, ""] + lines[i:], True

    return lines, False


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")

    changed = False

    lines = text.splitlines()
    lines, inserted = insert_opt_in_constant(lines)
    if inserted:
        text = "\n".join(lines) + "\n"
        changed = True

    parsed = ast.parse(text)
    target_linenos: list[int] = []
    for node in ast.walk(parsed):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("build_"):
            continue
        args = list(node.args.args) + list(node.args.kwonlyargs)
        if any(arg.arg == "foundry_features" for arg in args):
            target_linenos.append(node.lineno)

    if target_linenos:
        lines = text.splitlines()
        for lineno in sorted(target_linenos, reverse=True):
            sig_start = lineno - 1
            paren_balance = lines[sig_start].count("(") - lines[sig_start].count(")")
            sig_end = sig_start + 1
            while sig_end < len(lines) and paren_balance > 0:
                paren_balance += lines[sig_end].count("(") - lines[sig_end].count(")")
                sig_end += 1

            signature = "\n".join(lines[sig_start:sig_end])
            new_signature, sig_changed = remove_foundry_param_from_signature(signature)
            if not sig_changed:
                continue

            lines[sig_start:sig_end] = new_signature.split("\n")
            changed = True

        text = "\n".join(lines) + "\n"

    new_text = strip_foundry_docstring_sections(text)
    if new_text != text:
        text = new_text
        changed = True

    replacement = (
        'foundry_features=_get_foundry_features_opt_in_keys if '
        '(self.__class__.__name__.startswith("Beta") or self._config._allow_preview) else None, '
        '# type: ignore[attr-defined,arg-type]'
    )

    existing_replacement = (
        'foundry_features=_get_foundry_features_opt_in_keys if '
        '(self.__class__.__name__.startswith("Beta") or self._config._allow_preview) else None,'
    )

    if existing_replacement in text:
        text = text.replace(existing_replacement, replacement)
        changed = True

    new_text = RE_FOUNDRY_ASSIGN.sub(replacement, text)
    if new_text != text:
        text = new_text
        changed = True

    if changed:
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")

    return changed


def main() -> None:
    changed_files: list[str] = []

    for relative_path in TARGET_FILES:
        if process_file(relative_path):
            changed_files.append(str(relative_path))

    if changed_files:
        print("Updated files:")
        for file_path in changed_files:
            print(f"- {file_path}")
    else:
        print("No changes were needed.")


if __name__ == "__main__":
    main()
