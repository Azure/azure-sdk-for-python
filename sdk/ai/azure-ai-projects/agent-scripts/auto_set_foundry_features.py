#!/usr/bin/env python3
"""
Script to apply Foundry Features global opt-in changes to azure-ai-projects SDK.

Run from the azure-sdk-for-python/sdk/ai/azure-ai-projects/ directory:
    python agent-scripts/auto_set_foundry_features.py
"""

import re
import os

SYNC_OPS = os.path.join("azure", "ai", "projects", "operations", "_operations.py")
ASYNC_OPS = os.path.join("azure", "ai", "projects", "aio", "operations", "_operations.py")
MODELS_INIT = os.path.join("azure", "ai", "projects", "models", "__init__.py")
MODELS_ENUMS = os.path.join("azure", "ai", "projects", "models", "_enums.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_ff_type(line: str):
    """Parse the foundry_features parameter type from a parameter line.

    Returns a (ff_type, value) tuple or None.
    ff_type values:
      'agent_opt_in'     - Optional[Union[str, _models.AgentDefinitionOptInKeys]]
      'optional_literal' - Optional[Literal[FoundryFeaturesOptInKeys.SOME_VALUE]]
      'required_literal' - Literal[FoundryFeaturesOptInKeys.SOME_VALUE] (required)
    """
    if "Optional[Union[str, _models.AgentDefinitionOptInKeys]]" in line:
        return ("agent_opt_in", None)
    m = re.search(r"Optional\[Literal\[FoundryFeaturesOptInKeys\.(\w+)\]\]", line)
    if m:
        return ("optional_literal", m.group(1))
    m = re.search(r"\bLiteral\[FoundryFeaturesOptInKeys\.(\w+)\]", line)
    if m:
        return ("required_literal", m.group(1))
    return None


def make_local_var(ff_type: str, value, indent: str = "        ") -> str:
    """Create the _foundry_features local variable declaration line (with trailing newline)."""
    if ff_type == "agent_opt_in":
        return (
            f"{indent}_foundry_features: Optional[str] = "
            f"_get_agent_definition_opt_in_keys if self._config._allow_preview else None  # type: ignore\n"
        )
    elif ff_type == "optional_literal":
        return (
            f"{indent}_foundry_features: Optional[Literal[FoundryFeaturesOptInKeys.{value}]] = "
            f"FoundryFeaturesOptInKeys.{value} if self._config._allow_preview else None  # type: ignore\n"
        )
    elif ff_type == "required_literal":
        return (
            f"{indent}_foundry_features: Literal[FoundryFeaturesOptInKeys.{value}] = "
            f"FoundryFeaturesOptInKeys.{value}\n"
        )
    return ""


# ---------------------------------------------------------------------------
# Part 1 – Step 4: Add _foundry_features local variable to implementation methods
# ---------------------------------------------------------------------------


def add_local_vars_to_methods(content: str) -> str:
    """Add _foundry_features local variable to implementation methods
    that still have foundry_features in their signatures.

    Handles both @distributed_trace(d)-decorated and undecorated class methods.
    This must be called BEFORE remove_ff_from_signatures so that signatures
    still contain the type information needed to generate the local variable.
    """
    lines = content.split("\n")
    result = []

    # State tracking
    current_decorator = None  # 'overload' or 'impl'
    in_signature = False
    paren_depth = 0
    impl_ff_info = None  # (ff_type, ff_value) for current impl method
    pending_insertion = False
    in_docstring = False

    for line in lines:
        # ── Detect class-level decorator (exactly 4 spaces) ──────────────────
        m_dec = re.match(r"^    @(overload|distributed_trace(?:_async)?)\s*$", line)
        if m_dec:
            dec = m_dec.group(1)
            if dec == "overload":
                current_decorator = "overload"
            else:
                current_decorator = "impl"
                impl_ff_info = None
                pending_insertion = False
            in_signature = False
            result.append(line)
            continue

        # ── Detect method definition at class level (exactly 4 spaces) ───────
        # Also handles undecorated methods (current_decorator is None but not after @overload).
        # We treat any non-@overload method as a potential impl method.
        is_method_def = re.match(r"^    (?:async )?def ", line)
        if is_method_def and not in_signature:
            # If we just saw @overload, skip this method
            is_impl = current_decorator != "overload"
            in_signature = True
            paren_depth = line.count("(") - line.count(")")

            if is_impl:
                impl_ff_info = None
                pending_insertion = False
                # Scan this first line for foundry_features (single-line signature)
                if "foundry_features: " in line:
                    parsed = parse_ff_type(line)
                    if parsed:
                        impl_ff_info = parsed

            if paren_depth <= 0:
                in_signature = False
                if is_impl and impl_ff_info is not None:
                    pending_insertion = True
                current_decorator = None

            result.append(line)
            continue

        # ── Inside method signature ───────────────────────────────────────────
        if in_signature:
            paren_depth += line.count("(") - line.count(")")
            is_impl = current_decorator != "overload"

            if is_impl and "foundry_features: " in line:
                parsed = parse_ff_type(line)
                if parsed:
                    impl_ff_info = parsed

            if paren_depth <= 0:
                in_signature = False
                if is_impl and impl_ff_info is not None:
                    pending_insertion = True
                current_decorator = None

            result.append(line)
            continue

        # ── Track docstrings ──────────────────────────────────────────────────
        stripped = line.strip()
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = True
                content_after = stripped[3:]
                if '"""' in content_after or "'''" in content_after:
                    in_docstring = False
        else:
            if '"""' in line or "'''" in line:
                in_docstring = False

        # ── Insert local var at method body start ─────────────────────────────
        if pending_insertion and not in_docstring and not in_signature:
            body_start_patterns = [
                r"^        error_map: MutableMapping = \{",
                r"^        _headers = kwargs\.pop\(\"headers\", \{\}\) or \{\}",
                r"^        _headers = case_insensitive_dict\(",
            ]
            for pat in body_start_patterns:
                if re.match(pat, line):
                    ff_type, ff_value = impl_ff_info
                    local_var = make_local_var(ff_type, ff_value)
                    result.append(local_var.rstrip("\n"))
                    impl_ff_info = None
                    pending_insertion = False
                    break

        result.append(line)

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Part 1 – Steps 2+3: Remove foundry_features from non-build_ signatures
#                     and docstrings
# ---------------------------------------------------------------------------


def remove_ff_from_signatures(content: str) -> str:
    """Remove foundry_features parameter from non-build_ method signatures.

    Non-build_ parameters are at 8-space indent; build_ parameters are at
    4-space indent, so indentation distinguishes them.
    """
    # Sub-step A: Remove *,\n + foundry_features: when ff is the ONLY keyword-only arg
    # (i.e. **kwargs follows immediately after foundry_features)
    content = re.sub(
        r"\n        \*,\n        foundry_features: [^\n]+,\n(?=        \*\*kwargs)",
        "\n",
        content,
    )

    # Sub-step B: Remove standalone foundry_features: line at 8-space indent
    # (also covers cases where *,\n is NOT right above, meaning other kwargs exist)
    content = re.sub(
        r"\n        foundry_features: [^\n]+,\n",
        "\n",
        content,
    )

    # Sub-step C: Remove inline foundry_features (only kwarg) in class-method signatures.
    # Pattern: "self, ..., *, foundry_features: TYPE, **kwargs: Any" on one 8-space line.
    content = re.sub(
        r"(        self[^\n]*), \*, foundry_features: [^,\n]+, (\*\*kwargs: Any)",
        r"\1, \2",
        content,
    )

    return content


def remove_ff_from_docstrings(content: str) -> str:
    """Remove :keyword foundry_features: ... :paramtype foundry_features: blocks."""
    # The :keyword line is at 8-space indent; continuation lines at 9 spaces;
    # :paramtype line is at 8-space indent.
    content = re.sub(
        r"        :keyword foundry_features: [^\n]+\n(?:         [^\n]+\n)*"
        r"        :paramtype foundry_features: [^\n]+\n",
        "",
        content,
    )
    return content


# ---------------------------------------------------------------------------
# Part 1 – Step 4b: Replace foundry_features=foundry_features in build_ calls
# ---------------------------------------------------------------------------


def update_build_calls(content: str) -> str:
    """Replace foundry_features=foundry_features, with foundry_features=_foundry_features,."""
    return content.replace(
        "foundry_features=foundry_features,",
        "foundry_features=_foundry_features,",
    )


# ---------------------------------------------------------------------------
# Part 1 – Step 5: Update prepare_request paging next_link HttpRequest calls
# ---------------------------------------------------------------------------


def update_paging_requests(content: str) -> str:
    """In prepare_request(next_link=None) bodies that use _foundry_features,
    add Foundry-Features header to the next-link HttpRequest call."""

    OLD_HTTP_ARGS = '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'
    NEW_HTTP_ARGS = (
        '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params, '
        'headers={"Foundry-Features": _SERIALIZER.header("foundry_features", _foundry_features, "str")}'
    )

    def replace_if_ff(match: re.Match) -> str:
        body = match.group(1)
        suffix = match.group(2)
        if "foundry_features=_foundry_features," in body:
            body = body.replace(OLD_HTTP_ARGS, NEW_HTTP_ARGS)
        return body + suffix

    # Match from "def prepare_request(next_link=None):" up to (but not including)
    # "def extract_data" (sync) or "async def extract_data" (async).
    pattern = re.compile(
        r"(        def prepare_request\(next_link=None\):\n.*?)" r"(\n        (?:async )?def extract_data)",
        re.DOTALL,
    )
    return pattern.sub(replace_if_ff, content)


# ---------------------------------------------------------------------------
# Part 1 – Step 6: Fix any methods that call foundry_features=_foundry_features
#                  but never had _foundry_features defined (e.g. LRO wrappers)
# ---------------------------------------------------------------------------


def fix_missing_local_var(content: str) -> str:
    """Post-processing pass: inject _foundry_features local var into any class
    method body that uses foundry_features=_foundry_features but doesn't define
    the variable.

    This handles LRO wrapper methods (e.g. _begin_update_memories) that pass
    foundry_features through to an _initial method but never had foundry_features
    in their own signature.
    """
    lines = content.split("\n")
    result = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect start of a class method at 4-space indent
        if re.match(r"^    (?:async )?def ", line):
            # Collect all lines of this method body
            method_start = i
            method_lines = [line]
            j = i + 1
            # Collect until next def at same or lower indent level (or end)
            while j < len(lines):
                next_line = lines[j]
                # A new method or class starts at 4-space or 0-space indent
                if next_line and re.match(r"^(?:    (?:async )?def |class )", next_line):
                    break
                method_lines.append(next_line)
                j += 1

            # Check if this method uses foundry_features=_foundry_features
            # but does NOT define _foundry_features
            uses_ff = any("foundry_features=_foundry_features" in ml for ml in method_lines)
            defines_ff = any(
                re.match(r"\s+_foundry_features\s*[=:]", ml) for ml in method_lines
            )

            if uses_ff and not defines_ff:
                # Determine the value from the build_ call or _initial call in the body
                # Look for the type annotation from any foundry_features=_foundry_features call context
                # We infer the value from the build_ function being called
                ff_value = None
                for ml in method_lines:
                    m = re.search(
                        r"build_\w+_request\b|self\._\w+_initial\(",
                        ml,
                    )
                    if m:
                        # Try to find ff value from an existing _initial def in surrounding context
                        pass

                # Fallback: scan upstream already-built result for the _initial method's _foundry_features
                # Instead, find what foundry_features value is used in the associated _initial method
                # by scanning for the build_ function name
                build_func = None
                initial_func = None
                for ml in method_lines:
                    bm = re.search(r"build_(\w+)_request\s*\(", ml)
                    if bm:
                        build_func = bm.group(1)
                    im = re.search(r"self\.(_\w+_initial)\s*\(", ml)
                    if im:
                        initial_func = im.group(1)

                # Scan result (already processed lines) for the _foundry_features def
                # in the associated _initial method
                ff_type = "required_literal"
                ff_value = None
                if initial_func:
                    # Find _foundry_features assignment in the initial method we already emitted
                    for prev_line in result:
                        m = re.search(
                            r"_foundry_features:\s*(?:Optional\[)?Literal\[_?FoundryFeaturesOptInKeys\.(\w+)\]",
                            prev_line,
                        )
                        if m:
                            ff_value = m.group(1)
                            # Check if it's Optional
                            if "Optional" in prev_line:
                                ff_type = "optional_literal"
                            else:
                                ff_type = "required_literal"
                            # Keep looking for the most recent one (closest to this method)

                if ff_value is None and build_func:
                    # Derive from build function name: e.g. "beta_memory_stores_update_memories"
                    # → MEMORY_STORES_V1_PREVIEW
                    # Use a mapping of known patterns
                    if "memory_stores" in build_func:
                        ff_value = "MEMORY_STORES_V1_PREVIEW"
                        ff_type = "required_literal"

                if ff_value is None:
                    # Last resort: just copy from the last seen _foundry_features in result
                    for prev_line in reversed(result):
                        m = re.search(
                            r"_foundry_features:\s*(?:Optional\[)?Literal\[_?FoundryFeaturesOptInKeys\.(\w+)\]",
                            prev_line,
                        )
                        if m:
                            ff_value = m.group(1)
                            ff_type = "optional_literal" if "Optional" in prev_line else "required_literal"
                            break

                if ff_value is not None:
                    # Find the body start in method_lines and inject the local var
                    body_start_patterns = [
                        r"^        error_map: MutableMapping = \{",
                        r"^        _headers = kwargs\.pop\(\"headers\", \{\}\) or \{\}",
                        r"^        _headers = case_insensitive_dict\(",
                    ]
                    for k, ml in enumerate(method_lines):
                        for pat in body_start_patterns:
                            if re.match(pat, ml):
                                local_var = make_local_var(ff_type, ff_value).rstrip("\n")
                                method_lines.insert(k, local_var)
                                break
                        else:
                            continue
                        break

            result.extend(method_lines)
            i = j
            continue

        result.append(line)
        i += 1

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Main Part 1 orchestrator
# ---------------------------------------------------------------------------


def transform_ops_content_part1(content: str, is_sync: bool) -> str:
    """Apply all Part 1 transformations to an operations file."""

    # ── Step 1 (sync only): insert global var after the last top-level import
    if is_sync and "_get_agent_definition_opt_in_keys" not in content:
        old_import = "from ..models._enums import FoundryFeaturesOptInKeys\n"
        new_import = (
            "from ..models._enums import FoundryFeaturesOptInKeys\n"
            '_get_agent_definition_opt_in_keys: str = ",".join([key.value for key in _models.AgentDefinitionOptInKeys])\n'
        )
        content = content.replace(old_import, new_import, 1)

    # Split at first class definition so the header (build_ functions) is untouched
    class_match = re.search(r"^class ", content, re.MULTILINE)
    if class_match:
        header = content[: class_match.start()]
        classes = content[class_match.start() :]
    else:
        header = ""
        classes = content

    # ── Steps 3+4: Add local vars BEFORE removing from signatures
    classes = add_local_vars_to_methods(classes)

    # ── Step 2: Remove foundry_features from signatures
    classes = remove_ff_from_signatures(classes)

    # ── Step 3 (docstrings): Remove :keyword/:paramtype foundry_features blocks
    classes = remove_ff_from_docstrings(classes)

    # ── Step 4b: Update build_ call arguments
    classes = update_build_calls(classes)

    # ── Step 5: Update paging prepare_request HttpRequest calls
    classes = update_paging_requests(classes)

    # ── Step 6: Fix any LRO wrapper methods missing _foundry_features
    classes = fix_missing_local_var(classes)

    return header + classes


# ---------------------------------------------------------------------------
# Part 2 – Rename internal enum classes and fix imports everywhere
# ---------------------------------------------------------------------------


def apply_part2(
    sync_ops: str,
    async_ops: str,
    models_init: str,
    models_enums: str,
):
    """Rename AgentDefinitionOptInKeys → _AgentDefinitionOptInKeys and
    FoundryFeaturesOptInKeys → _FoundryFeaturesOptInKeys everywhere."""

    # ── _enums.py: rename the two classes ────────────────────────────────────
    models_enums = models_enums.replace(
        "class AgentDefinitionOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):",
        "class _AgentDefinitionOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):",
    )
    models_enums = models_enums.replace(
        "class FoundryFeaturesOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):",
        "class _FoundryFeaturesOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):",
    )

    # ── models/__init__.py: remove from imports and __all__ ──────────────────
    models_init = re.sub(r"    AgentDefinitionOptInKeys,\n", "", models_init)
    models_init = re.sub(r"    FoundryFeaturesOptInKeys,\n", "", models_init)
    models_init = re.sub(r'    "AgentDefinitionOptInKeys",\n', "", models_init)
    models_init = re.sub(r'    "FoundryFeaturesOptInKeys",\n', "", models_init)

    # ── Sync _operations.py ──────────────────────────────────────────────────
    # Update import to bring in both renamed private classes
    sync_ops = sync_ops.replace(
        "from ..models._enums import FoundryFeaturesOptInKeys",
        "from ..models._enums import _AgentDefinitionOptInKeys, _FoundryFeaturesOptInKeys",
    )
    # Rename FoundryFeaturesOptInKeys → _FoundryFeaturesOptInKeys
    # (use negative lookbehind to avoid double-prefixing _FoundryFeaturesOptInKeys)
    sync_ops = re.sub(r"(?<!_)FoundryFeaturesOptInKeys", "_FoundryFeaturesOptInKeys", sync_ops)
    # Rename _models.AgentDefinitionOptInKeys → _AgentDefinitionOptInKeys
    sync_ops = sync_ops.replace("_models.AgentDefinitionOptInKeys", "_AgentDefinitionOptInKeys")

    # ── Async _operations.py ─────────────────────────────────────────────────
    # Step 1: replace _models.AgentDefinitionOptInKeys → _AgentDefinitionOptInKeys BEFORE regex
    async_ops = async_ops.replace("_models.AgentDefinitionOptInKeys", "_AgentDefinitionOptInKeys")
    # Step 2: update import line to bring in both private classes
    # Original may have either "FoundryFeaturesOptInKeys" alone or both names
    async_ops = async_ops.replace(
        "from ...models._enums import AgentDefinitionOptInKeys, FoundryFeaturesOptInKeys",
        "from ...models._enums import _AgentDefinitionOptInKeys, _FoundryFeaturesOptInKeys",
    )
    async_ops = async_ops.replace(
        "from ...models._enums import FoundryFeaturesOptInKeys",
        "from ...models._enums import _AgentDefinitionOptInKeys, _FoundryFeaturesOptInKeys",
    )
    # Step 3: rename any remaining bare references (negative lookbehind avoids double-prefixing)
    async_ops = re.sub(r"(?<!_)FoundryFeaturesOptInKeys", "_FoundryFeaturesOptInKeys", async_ops)
    async_ops = re.sub(r"(?<!_)AgentDefinitionOptInKeys", "_AgentDefinitionOptInKeys", async_ops)

    return sync_ops, async_ops, models_init, models_enums


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("Reading files…")
    sync_ops = read_file(SYNC_OPS)
    async_ops = read_file(ASYNC_OPS)
    models_init = read_file(MODELS_INIT)
    models_enums = read_file(MODELS_ENUMS)

    # ── Part 1 ────────────────────────────────────────────────────────────────
    print("Applying Part 1 to sync operations file…")
    sync_ops = transform_ops_content_part1(sync_ops, is_sync=True)

    print("Applying Part 1 to async operations file…")
    async_ops = transform_ops_content_part1(async_ops, is_sync=False)

    # ── Part 2 ────────────────────────────────────────────────────────────────
    print("Applying Part 2 (rename internal enum classes)…")
    sync_ops, async_ops, models_init, models_enums = apply_part2(sync_ops, async_ops, models_init, models_enums)

    # ── Write results ─────────────────────────────────────────────────────────
    print("Writing files…")
    write_file(SYNC_OPS, sync_ops)
    write_file(ASYNC_OPS, async_ops)
    write_file(MODELS_INIT, models_init)
    write_file(MODELS_ENUMS, models_enums)

    print("Done.")


if __name__ == "__main__":
    main()
