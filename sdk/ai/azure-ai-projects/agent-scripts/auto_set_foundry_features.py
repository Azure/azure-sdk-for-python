#!/usr/bin/env python3
"""Apply Foundry preview feature updates to generated operations files.

Run this script from:
  sdk/ai/azure-ai-projects

This script only edits:
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
    '_get_foundry_features_opt_in_keys: str = ",".join([key.value for key in '
    "_models.AgentDefinitionOptInKeys] + [key.value for key in _models.FoundryFeaturesOptInKeys])"
)

FOUNDY_ASSIGN_OLD_RE = re.compile(r"foundry_features\s*=\s*foundry_features,")

PAGING_GET_OLD = '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'
PAGING_GET_NEW = (
    '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), '
    'params=_next_request_params, headers={"Foundry-Features": '
    '_SERIALIZER.header("foundry_features", foundry_features, "str")}'
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
        has_non_kwargs_after = any(p.strip() and not p.strip().startswith("**") for p in kept_parts[idx + 1 :])
        if not has_non_kwargs_after:
            kept_parts.pop(idx)

    new_params = ",".join(kept_parts)
    return f"{head}{new_params}{tail}", True


def insert_opt_in_constant(lines: list[str]) -> tuple[list[str], bool]:
    if any(line.strip() == INSERT_LINE for line in lines):
        return lines, False

    for i, line in enumerate(lines):
        if line.startswith("JSON = MutableMapping"):
            return lines[:i] + [INSERT_LINE, ""] + lines[i:], True

    return lines, False


def get_target_functions(parsed: ast.AST) -> list[tuple[str, int, int]]:
    targets: list[tuple[str, int, int]] = []

    for node in ast.walk(parsed):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("build_"):
            continue

        args = list(node.args.args) + list(node.args.kwonlyargs)
        if any(arg.arg == "foundry_features" for arg in args):
            if node.end_lineno is None:
                continue
            targets.append((node.name, node.lineno, node.end_lineno))

    return targets


def strip_foundry_from_signatures(text: str, target_line_starts: set[int]) -> tuple[str, bool]:
    lines = text.splitlines()
    changed = False

    for lineno in sorted(target_line_starts, reverse=True):
        sig_start = lineno - 1
        if sig_start < 0 or sig_start >= len(lines):
            continue

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

    if not changed:
        return text, False

    return "\n".join(lines) + "\n", True


def strip_foundry_docstring_lines(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    original_len = len(lines)
    filtered = [
        line
        for line in lines
        if not line.lstrip().startswith(":keyword foundry_features:")
        and not line.lstrip().startswith(":paramtype foundry_features:")
    ]
    changed = len(filtered) != original_len
    if not changed:
        return text, False
    return "\n".join(filtered) + "\n", True


def replace_foundry_assignments(text: str) -> tuple[str, bool]:
    replacement_core = (
        "foundry_features=_get_foundry_features_opt_in_keys if "
        '(self.__class__.__name__.startswith("Beta") or self._config._allow_preview) else None,'
    )
    replacement = f"{replacement_core} # type: ignore[attr-defined,arg-type]"

    # Upgrade already-replaced lines to include ignore markers.
    updated_text = text.replace(replacement_core, replacement)
    new_text = FOUNDY_ASSIGN_OLD_RE.sub(replacement, updated_text)
    return new_text, new_text != text


def replace_paging_get_lines(text: str, target_names: set[str]) -> tuple[str, bool]:
    parsed = ast.parse(text)
    lines = text.splitlines()
    changed = False

    for node in sorted(
        (n for n in ast.walk(parsed) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
        key=lambda n: n.lineno,
        reverse=True,
    ):
        if node.name not in target_names or node.name.startswith("build_"):
            continue
        if node.end_lineno is None:
            continue

        start = node.lineno - 1
        end = node.end_lineno
        block = "\n".join(lines[start:end])

        if "def prepare_request(next_link=None):" not in block:
            continue
        if PAGING_GET_OLD not in block:
            continue

        updated = block.replace(PAGING_GET_OLD, PAGING_GET_NEW)
        if updated != block:
            lines[start:end] = updated.split("\n")
            changed = True

    if not changed:
        return text, False

    return "\n".join(lines) + "\n", True


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False

    lines = text.splitlines()
    lines, inserted = insert_opt_in_constant(lines)
    if inserted:
        text = "\n".join(lines) + "\n"
        changed = True

    parsed_before = ast.parse(text)
    targets = get_target_functions(parsed_before)
    target_line_starts = {lineno for _, lineno, _ in targets}
    target_names = {name for name, _, _ in targets}

    new_text, did_change = strip_foundry_from_signatures(text, target_line_starts)
    if did_change:
        text = new_text
        changed = True

    new_text, did_change = strip_foundry_docstring_lines(text)
    if did_change:
        text = new_text
        changed = True

    new_text, did_change = replace_foundry_assignments(text)
    if did_change:
        text = new_text
        changed = True

    new_text, did_change = replace_paging_get_lines(text, target_names)
    if did_change:
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
