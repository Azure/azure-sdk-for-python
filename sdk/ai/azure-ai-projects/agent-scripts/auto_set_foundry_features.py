from __future__ import annotations

import ast
import re
from pathlib import Path

TARGET_FILES = [
    Path("azure/ai/projects/aio/operations/_operations.py"),
    Path("azure/ai/projects/operations/_operations.py"),
]

OPT_IN_CONST = (
    '_get_foundry_features_opt_in_keys: str = ",".join([key.value for key in '
    "_models.AgentDefinitionOptInKeys] + [key.value for key in _models.FoundryFeaturesOptInKeys])"
)

FOUNDRY_ARG_OLD = "foundry_features=foundry_features,"
FOUNDRY_ARG_NEW = (
    "foundry_features=cast(Any, _get_foundry_features_opt_in_keys if "
    '(self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None),'
)

FOUNDRY_ARG_OLD_AFTER_FIRST_PASS = (
    "foundry_features=_get_foundry_features_opt_in_keys if "
    '(self.__class__.__name__.startswith("Beta") or self._config._allow_preview) else None,'
)

FOUNDRY_ARG_OLD_AFTER_FIRST_PASS_GETATTR = (
    "foundry_features=_get_foundry_features_opt_in_keys if "
    '(self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None,'
)

NEXT_LINK_OLD = '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'
NEXT_LINK_NEW = (
    '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), '
    'params=_next_request_params, headers={"Foundry-Features": '
    '_SERIALIZER.header("foundry_features", cast(Any, _get_foundry_features_opt_in_keys if '
    '(self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None), "str")}'
)

NEXT_LINK_OLD_AFTER_FIRST_PASS = (
    '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), '
    'params=_next_request_params, headers={"Foundry-Features": '
    '_SERIALIZER.header("foundry_features", foundry_features, "str")}'
)


def _apply_global_rewrites(text: str) -> str:
    text = text.replace("self._config._allow_preview", 'getattr(self._config, "_allow_preview", False)')

    # Normalize all previously generated foundry_features argument variants.
    text = text.replace(FOUNDRY_ARG_OLD, FOUNDRY_ARG_NEW)
    text = text.replace(FOUNDRY_ARG_OLD_AFTER_FIRST_PASS, FOUNDRY_ARG_NEW)
    text = text.replace(FOUNDRY_ARG_OLD_AFTER_FIRST_PASS_GETATTR, FOUNDRY_ARG_NEW)
    text = re.sub(
        r"foundry_features=_get_foundry_features_opt_in_keys if "
        r'\(self\.__class__\.__name__\.startswith\("Beta"\) or '
        r'getattr\(self\._config, "_allow_preview", False\)\) else None,',
        FOUNDRY_ARG_NEW,
        text,
    )

    # Normalize prepare_request next-link call variants.
    text = text.replace(NEXT_LINK_OLD, NEXT_LINK_NEW)
    text = text.replace(NEXT_LINK_OLD_AFTER_FIRST_PASS, NEXT_LINK_NEW)
    text = text.replace(
        'headers={"Foundry-Features": _SERIALIZER.header("foundry_features", foundry_features, "str")}',
        'headers={"Foundry-Features": _SERIALIZER.header("foundry_features", cast(Any, _get_foundry_features_opt_in_keys if (self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None), "str")}',
    )
    text = text.replace(
        'headers={"Foundry-Features": self._serialize.header("foundry_features", foundry_features, "str")}',
        'headers={"Foundry-Features": _SERIALIZER.header("foundry_features", cast(Any, _get_foundry_features_opt_in_keys if (self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None), "str")}',
    )

    text = re.sub(
        r"^[ \t]*foundry_features = _get_foundry_features_opt_in_keys if "
        r'\(self\.__class__\.__name__\.startswith\("Beta"\) or '
        r'getattr\(self\._config, "_allow_preview", False\)\) else None\r?\n',
        "",
        text,
        flags=re.MULTILINE,
    )

    return text


def _ensure_serializer_instance(text: str, newline: str) -> str:
    if "_SERIALIZER = Serializer()" in text:
        return text

    lines = text.splitlines(keepends=True)
    for idx, line in enumerate(lines):
        if line.startswith("class "):
            insertion = [
                "_SERIALIZER = Serializer()" + newline,
                "_SERIALIZER.client_side_validation = False" + newline,
                newline,
            ]
            lines[idx:idx] = insertion
            return "".join(lines)

    return text


def _detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _insert_opt_in_const(text: str, newline: str) -> str:
    if OPT_IN_CONST in text:
        return text

    lines = text.splitlines(keepends=True)

    for idx, line in enumerate(lines):
        if line.startswith("JSON = MutableMapping"):
            insertion = [OPT_IN_CONST + newline, newline]
            lines[idx:idx] = insertion
            return "".join(lines)

    last_import_idx = -1
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_idx = idx

    if last_import_idx >= 0:
        insertion = [newline, OPT_IN_CONST + newline]
        lines[last_import_idx + 1 : last_import_idx + 1] = insertion

    return "".join(lines)


def _split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1

        if ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)

    parts.append("".join(current))
    return parts


def _remove_foundry_from_signature(signature_text: str) -> str:
    open_idx = signature_text.find("(")
    if open_idx < 0:
        return signature_text

    depth = 0
    close_idx = -1
    for idx, ch in enumerate(signature_text[open_idx:], start=open_idx):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                close_idx = idx
                break

    if close_idx < 0:
        return signature_text

    params_text = signature_text[open_idx + 1 : close_idx]
    params = _split_top_level_commas(params_text)

    filtered: list[str] = []
    for param in params:
        stripped = param.strip()
        if stripped.startswith("foundry_features:"):
            continue
        filtered.append(param)

    # Remove a bare "*" marker if it would be followed only by **kwargs or nothing.
    changed = True
    while changed:
        changed = False
        for idx, token in enumerate(filtered):
            if token.strip() != "*":
                continue
            next_nonempty = ""
            for candidate in filtered[idx + 1 :]:
                if candidate.strip():
                    next_nonempty = candidate.strip()
                    break
            if not next_nonempty or next_nonempty.startswith("**"):
                del filtered[idx]
                changed = True
                break

    new_params_text = ",".join(filtered)
    return signature_text[: open_idx + 1] + new_params_text + signature_text[close_idx:]


def _find_signature_end(block_text: str) -> int:
    depth = 0
    seen_open = False
    for idx, ch in enumerate(block_text):
        if ch == "(":
            depth += 1
            seen_open = True
        elif ch == ")":
            depth -= 1
        elif ch == ":" and seen_open and depth == 0:
            return idx + 1
    return -1


def _remove_foundry_docstring_lines(block_text: str) -> str:
    lines = block_text.splitlines(keepends=True)
    out: list[str] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        if ":keyword foundry_features:" in line:
            idx += 1
            while idx < len(lines):
                if ":paramtype foundry_features:" in lines[idx]:
                    idx += 1
                    break
                idx += 1
            continue

        out.append(line)
        idx += 1

    return "".join(out)


def _remove_bad_first_pass_helper_lines(block_text: str) -> str:
    bad_line_1 = (
        "foundry_features = _get_foundry_features_opt_in_keys if "
        '(self.__class__.__name__.startswith("Beta") or self._config._allow_preview) else None'
    )
    bad_line_2 = (
        "foundry_features = _get_foundry_features_opt_in_keys if "
        '(self.__class__.__name__.startswith("Beta") or getattr(self._config, "_allow_preview", False)) else None'
    )

    lines = block_text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == bad_line_1 or stripped == bad_line_2:
            continue
        out.append(line)
    return "".join(out)


def _get_function_block_indent(block_text: str) -> str:
    first_line = block_text.splitlines()[0]
    return first_line[: len(first_line) - len(first_line.lstrip(" "))]


def _transform_function_block(block_text: str) -> str:
    signature_end = _find_signature_end(block_text)
    if signature_end > 0:
        signature_text = block_text[:signature_end]
        rest = block_text[signature_end:]
        signature_text = _remove_foundry_from_signature(signature_text)
        block_text = signature_text + rest

    block_text = _remove_foundry_docstring_lines(block_text)
    block_text = _remove_bad_first_pass_helper_lines(block_text)

    block_text = block_text.replace(FOUNDRY_ARG_OLD, FOUNDRY_ARG_NEW)
    block_text = block_text.replace(FOUNDRY_ARG_OLD_AFTER_FIRST_PASS, FOUNDRY_ARG_NEW)
    block_text = block_text.replace(FOUNDRY_ARG_OLD_AFTER_FIRST_PASS_GETATTR, FOUNDRY_ARG_NEW)

    if "def prepare_request(next_link=None):" in block_text:
        block_text = block_text.replace(NEXT_LINK_OLD, NEXT_LINK_NEW)
        block_text = block_text.replace(NEXT_LINK_OLD_AFTER_FIRST_PASS, NEXT_LINK_NEW)

    return block_text


def _node_has_foundry_features_arg(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    all_args = [
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs,
    ]
    return any(arg.arg == "foundry_features" for arg in all_args)


def _apply_to_file(path: Path) -> bool:
    original_text = path.read_text(encoding="utf-8")
    newline = _detect_newline(original_text)

    text = _insert_opt_in_const(original_text, newline)
    text = _ensure_serializer_instance(text, newline)
    text = _apply_global_rewrites(text)
    tree = ast.parse(text)

    targets: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("build_"):
                continue
            if _node_has_foundry_features_arg(node):
                targets.append(node)

    if not targets and text == original_text:
        return False

    lines = text.splitlines(keepends=True)

    for node in sorted(targets, key=lambda n: n.lineno, reverse=True):
        start = node.lineno - 1
        end = node.end_lineno
        block_text = "".join(lines[start:end])
        block_text = _transform_function_block(block_text)
        lines[start:end] = [block_text]

    new_text = "".join(lines)
    if new_text != original_text:
        path.write_text(new_text, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    root = Path.cwd()
    changed_any = False

    for relative_path in TARGET_FILES:
        full_path = root / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Target file not found: {relative_path}")
        changed = _apply_to_file(full_path)
        print(f"{relative_path}: {'modified' if changed else 'no changes'}")
        changed_any = changed_any or changed

    print("Done." if changed_any else "Done (no updates needed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
