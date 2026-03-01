#!/usr/bin/env python3
"""
auto_set_foundry_features.py

Script to apply the foundry-features opt-in changes to the generated operations files.

Run from: azure-sdk-for-python/sdk/ai/azure-ai-projects

Steps applied to each target file:
  1. Insert _get_foundry_features_opt_in_keys constant after the last import statement.
  2. Remove the 'foundry_features' parameter from all non-build_ method signatures.
     Also remove the corresponding :keyword / :paramtype docstring entries.
  3. Add a local variable 'foundry_features' at the top of each implementation method body
     (required params → fixed string; optional → conditional on allow_preview flag).
  4. In any nested 'def prepare_request(next_link=None):' function, ensure the paginated
     GET request includes the Foundry-Features header.
"""

import ast
import re
import os
import sys

# ── Constants ───────────────────────────────────────────────────────────────

FF_OPT_IN_LINE = (
    '_get_foundry_features_opt_in_keys: str = ",".join('
    '[key.value for key in _models.AgentDefinitionOptInKeys] + '
    '[key.value for key in _models.FoundryFeaturesOptInKeys])'
)

TARGET_FILES = [
    os.path.join("azure", "ai", "projects", "aio", "operations", "_operations.py"),
    os.path.join("azure", "ai", "projects", "operations", "_operations.py"),
]

# ── Entry point ──────────────────────────────────────────────────────────────


def main():
    # Locate the azure-ai-projects root (one level up from agent-scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    for rel_path in TARGET_FILES:
        filepath = os.path.join(base_dir, rel_path)
        if not os.path.exists(filepath):
            print(f"WARNING: File not found: {filepath}")
            continue
        process_file(filepath)

    print("\nAll done!")


# ── File-level processing ────────────────────────────────────────────────────


def process_file(filepath):
    print(f"\nProcessing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Idempotency guard
    if "_get_foundry_features_opt_in_keys" in content:
        print("  Already processed (found _get_foundry_features_opt_in_keys). Skipping.")
        return

    # Parse AST to find functions that need changes
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"  ERROR: Cannot parse file: {e}")
        return

    lines = content.splitlines(keepends=False)
    original_len = len(lines)
    ends_with_newline = content.endswith("\n")

    # Collect all functions with a 'foundry_features' parameter that aren't build_ functions
    functions_to_process = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("build_"):
            continue

        found, is_optional = _find_ff_in_args(node)
        if not found:
            continue

        is_overload = any(
            (isinstance(d, ast.Name) and d.id == "overload")
            or (isinstance(d, ast.Attribute) and d.attr == "overload")
            for d in node.decorator_list
        )

        has_docstring = False
        docstring_end_1based = None
        if node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and hasattr(first, "value")
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                has_docstring = True
                docstring_end_1based = first.end_lineno  # 1-based

        func_length = node.end_lineno - node.lineno + 1
        functions_to_process.append(
            {
                "name": node.name,
                "lineno": node.lineno,          # 1-based
                "end_lineno": node.end_lineno,  # 1-based
                "func_length": func_length,
                "is_optional": is_optional,
                "is_overload": is_overload,
                "has_docstring": has_docstring,
                "docstring_end_1based": docstring_end_1based,
            }
        )

    # Process bottom-to-top so earlier line numbers stay valid
    functions_to_process.sort(key=lambda x: x["lineno"], reverse=True)

    print(f"  Found {len(functions_to_process)} function(s) to process")
    for fi in functions_to_process:
        opt = "optional" if fi["is_optional"] else "required"
        ov = " [overload]" if fi["is_overload"] else ""
        print(f"    - {fi['name']}() line {fi['lineno']} ({opt}){ov}")

    for fi in functions_to_process:
        lines = _apply_function_changes(lines, fi)

    # Step 1: Insert the opt-in-keys constant right after the last import statement
    lines = _insert_ff_constant(lines)

    new_content = "\n".join(lines)
    if ends_with_newline and not new_content.endswith("\n"):
        new_content += "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  Saved ({len(lines)} lines, was {original_len} lines)")


# ── AST helpers ──────────────────────────────────────────────────────────────


def _find_ff_in_args(node):
    """Return (found: bool, is_optional: bool) for foundry_features parameter."""
    for i, arg in enumerate(node.args.kwonlyargs):
        if arg.arg == "foundry_features":
            return True, node.args.kw_defaults[i] is not None

    for i, arg in enumerate(node.args.args):
        if arg.arg == "foundry_features":
            num_without_default = len(node.args.args) - len(node.args.defaults)
            return True, i >= num_without_default

    return False, False


# ── Constant insertion ────────────────────────────────────────────────────────


def _insert_ff_constant(lines):
    """Find the last top-level import/from line and insert the constant right after it."""
    last_import_0 = -1
    for i, line in enumerate(lines):
        if line and not line[0].isspace():
            if line.startswith("from ") or line.startswith("import "):
                last_import_0 = i

    if last_import_0 == -1:
        raise ValueError("No import statements found in file")

    lines.insert(last_import_0 + 1, FF_OPT_IN_LINE)
    return lines


# ── Per-function changes ──────────────────────────────────────────────────────


def _apply_function_changes(lines, fi):
    start_0 = fi["lineno"] - 1   # 0-indexed start of the 'def' line
    is_optional = fi["is_optional"]
    is_overload = fi["is_overload"]
    has_docstring = fi["has_docstring"]
    func_length = fi["func_length"]  # original line count of the function

    # Step 2a – Remove foundry_features from the function signature
    sig_end_0 = _find_signature_end_idx(lines, start_0)
    lines, sig_line_removed = _remove_ff_from_signature(lines, start_0, sig_end_0)

    # Compute a safe upper bound for the function's content in the (possibly modified) lines
    search_end = min(start_0 + func_length + 10, len(lines))

    # Step 2b – Remove :keyword foundry_features: … :paramtype foundry_features: from docstring
    if has_docstring:
        lines = _remove_ff_from_docstring(lines, start_0, search_end)

    # Step 3 – Add local variable at top of implementation method body
    if not is_overload and has_docstring:
        lines = _add_ff_local_var(lines, start_0, search_end, is_optional)

    # Step 4 – Fix prepare_request(next_link=None) if present
    if not is_overload:
        lines = _fix_prepare_request(lines, start_0, search_end)

    return lines


# ── Signature handling ────────────────────────────────────────────────────────


def _find_signature_end_idx(lines, func_start_0):
    """Return 0-based index of the line containing the closing ')' of the function signature."""
    depth = 0
    started = False
    for i in range(func_start_0, len(lines)):
        for ch in lines[i]:
            if ch == "(":
                depth += 1
                started = True
            elif ch == ")":
                depth -= 1
                if started and depth == 0:
                    return i
    return func_start_0


def _remove_ff_from_signature(lines, start_0, sig_end_0):
    """
    Remove the foundry_features parameter from the function signature.
    Returns (lines, line_removed) where line_removed indicates whether a line was deleted.
    """
    for i in range(start_0, sig_end_0 + 1):
        line = lines[i]
        stripped = line.strip()

        # Case A: foundry_features is the sole parameter on this line
        #   e.g. "        foundry_features: Optional[str] = None,"
        if re.match(r"^foundry_features\s*:", stripped) and "def " not in line:
            del lines[i]
            # If foundry_features was the only kwonly arg, the preceding '*,'
            # separator would now be orphaned (SyntaxError). Remove it too.
            if i > 0 and lines[i - 1].strip() == "*,":
                next_stripped = lines[i].strip() if i < len(lines) else ""
                if next_stripped.startswith("**") or next_stripped == ")":
                    del lines[i - 1]
            return lines, True

        # Case B: foundry_features shares a line with other parameters
        #   e.g. "self, name: str, *, foundry_features: str, **kwargs: Any"
        if "foundry_features" in line and re.search(r"\bfoundry_features\s*:", line):
            # Make sure it is not a docstring line
            if ":keyword " not in line and ":paramtype " not in line:
                new_line = _remove_ff_from_mixed_line(line)
                if new_line != line:
                    lines[i] = new_line
                    return lines, False

    return lines, False


def _remove_ff_from_mixed_line(line):
    """
    Remove 'foundry_features: TYPE[= DEFAULT], ' from a line that also has other parameters.
    Uses bracket-depth counting to handle complex type annotations.
    """
    idx = line.find("foundry_features:")
    if idx == -1:
        return line

    # Walk forward from after "foundry_features:" to find the end of this parameter
    depth = 0
    pos = idx + len("foundry_features:")
    while pos < len(line):
        c = line[pos]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                break           # hit the closing paren of the parameter list
            depth -= 1
        elif c == "," and depth == 0:
            pos += 1            # consume comma
            if pos < len(line) and line[pos] == " ":
                pos += 1        # consume one trailing space
            break
        pos += 1

    result = line[:idx] + line[pos:]
    # Clean up unlikely double-comma artifact
    result = re.sub(r",\s*,", ",", result)
    return result


# ── Docstring handling ────────────────────────────────────────────────────────


def _remove_ff_from_docstring(lines, func_start_0, search_end):
    """Delete the ':keyword foundry_features:' … ':paramtype foundry_features:' block."""
    kw_idx = None
    pt_idx = None

    for i in range(func_start_0, min(search_end, len(lines))):
        if ":keyword foundry_features:" in lines[i]:
            kw_idx = i
        if kw_idx is not None and ":paramtype foundry_features:" in lines[i]:
            pt_idx = i
            break

    if kw_idx is not None and pt_idx is not None:
        del lines[kw_idx : pt_idx + 1]

    return lines


# ── Local variable insertion ─────────────────────────────────────────────────


def _find_docstring_end_idx(lines, func_start_0, search_end):
    """Return the 0-based index of the line containing the closing ''' or \"\"\" of the docstring."""
    in_docstring = False
    quote_char = None

    for i in range(func_start_0, min(search_end, len(lines))):
        stripped = lines[i].strip()
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote_char = stripped[:3]
                rest = stripped[3:]
                if quote_char in rest:
                    return i          # single-line docstring
                in_docstring = True
        else:
            if quote_char and quote_char in stripped:
                return i              # found the closing triple-quote

    return None


def _add_ff_local_var(lines, func_start_0, search_end, is_optional):
    """Insert the foundry_features local variable right after the closing docstring line."""
    doc_end_i = _find_docstring_end_idx(lines, func_start_0, search_end)
    if doc_end_i is None:
        print(f"    WARNING: Could not find docstring end for function at line {func_start_0 + 1}")
        return lines

    # Derive body indentation from the 'def' line's indentation + 4 spaces
    def_line = lines[func_start_0]
    def_indent = len(def_line) - len(def_line.lstrip())
    body_indent = " " * (def_indent + 4)

    if is_optional:
        var_line = (
            f"{body_indent}foundry_features: Optional[str] = "
            f"_get_foundry_features_opt_in_keys "
            f'if (self.__class__.__name__.startswith("Beta") or '
            f"self._config._allow_preview) else None  # type: ignore"
        )
    else:
        var_line = f"{body_indent}foundry_features: str = _get_foundry_features_opt_in_keys"

    lines.insert(doc_end_i + 1, var_line)
    return lines


# ── prepare_request fix ───────────────────────────────────────────────────────


def _fix_prepare_request(lines, func_start_0, search_end):
    """
    Within a nested 'def prepare_request(next_link=None):' function, find the
    HttpRequest("GET", ..., params=_next_request_params) call that lacks a Foundry-Features
    header and add one.

    Looks for a single-line pattern of the form:
        "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params
    (without a trailing 'headers=') and appends the header argument.
    """
    # Locate the nested prepare_request function
    prepare_req_start = None
    for i in range(func_start_0, min(search_end, len(lines))):
        if re.search(r"def\s+prepare_request\s*\(\s*next_link\s*=\s*None\s*\)\s*:", lines[i]):
            prepare_req_start = i
            break

    if prepare_req_start is None:
        return lines

    # Look for the specific single-line HttpRequest pattern (no 'headers=' yet)
    for i in range(prepare_req_start, min(prepare_req_start + 60, len(lines))):
        if i >= len(lines):
            break
        line = lines[i]
        if (
            '"GET"' in line
            and "urllib.parse.urljoin(next_link, _parsed_next_link.path)" in line
            and "params=_next_request_params" in line
            and "headers=" not in line
        ):
            old_pattern = (
                '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), '
                "params=_next_request_params"
            )
            new_pattern = (
                '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), '
                "params=_next_request_params, "
                'headers={"Foundry-Features": _SERIALIZER.header("foundry_features", foundry_features, "str")}'
            )
            lines[i] = line.replace(old_pattern, new_pattern)
            break

    return lines


# ── Main guard ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
