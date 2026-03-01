#!/usr/bin/env python3
"""
Auto-set Foundry Features script.

Modifies the following two files to implement a global opt-in flag for Foundry preview features:
  azure/ai/projects/operations/_operations.py
  azure/ai/projects/aio/operations/_operations.py

Changes applied to each file:
  Step 1: Insert _get_agent_definition_opt_in_keys variable after last import.
  Step 2: Remove 'foundry_features' from non-build_ method signatures and docstrings.
  Step 3: Insert '_foundry_features' local variable in implementation method bodies.
  Step 4: Replace 'foundry_features=foundry_features' with 'foundry_features=_foundry_features'
          in build_ function calls.
  Step 5: Add Foundry-Features header to the GET line inside prepare_request() for list methods
          that had foundry_features.

Run this script from the folder:
  \\azure-sdk-for-python\\sdk\\ai\\azure-ai-projects
"""

import os
import re
import sys

FILES = [
    os.path.join("azure", "ai", "projects", "operations", "_operations.py"),
    os.path.join("azure", "ai", "projects", "aio", "operations", "_operations.py"),
]

GLOBAL_VAR_LINE = (
    "_get_agent_definition_opt_in_keys: str = " '",".join([key.value for key in _models.AgentDefinitionOptInKeys])\n'
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_ff_info(line):
    """Parse foundry_features annotation from a line containing 'foundry_features: '.

    Returns (kind, value) where kind is one of:
      'union_optional'   -> Optional[Union[str, _models.AgentDefinitionOptInKeys]] = None
      'literal_optional' -> Optional[Literal[FoundryFeaturesOptInKeys.X]] = None
      'literal_required' -> Literal[FoundryFeaturesOptInKeys.X]   (required, no default)
    and value is the enum member name (e.g. 'EVALUATIONS_V1_PREVIEW') or None for union_optional.
    """
    if "Optional[Union[str, _models.AgentDefinitionOptInKeys]]" in line:
        return "union_optional", None

    m = re.search(r"Optional\[Literal\[FoundryFeaturesOptInKeys\.(\w+)\]\]", line)
    if m:
        return "literal_optional", m.group(1)

    m = re.search(r"\bLiteral\[FoundryFeaturesOptInKeys\.(\w+)\]", line)
    if m:
        return "literal_required", m.group(1)

    return None, None


def make_local_var(kind, value, body_indent):
    """Generate the _foundry_features local variable declaration line."""
    if kind == "union_optional":
        return (
            f"{body_indent}_foundry_features: Optional[str] = "
            f"_get_agent_definition_opt_in_keys if self._config._allow_preview else None"
            f"  # type: ignore\n"
        )
    if kind == "literal_optional":
        return (
            f"{body_indent}_foundry_features: Optional[Literal[FoundryFeaturesOptInKeys.{value}]] = "
            f"FoundryFeaturesOptInKeys.{value} if self._config._allow_preview else None"
            f"  # type: ignore\n"
        )
    if kind == "literal_required":
        return (
            f"{body_indent}_foundry_features: Literal[FoundryFeaturesOptInKeys.{value}]"
            f" = FoundryFeaturesOptInKeys.{value}\n"
        )
    return None


# ---------------------------------------------------------------------------
# Step 1 – insert the global variable after the last import statement
# ---------------------------------------------------------------------------


def step1_insert_global(lines):
    """Insert _get_agent_definition_opt_in_keys after the last top-level import."""
    # Skip if the variable is already present
    for line in lines:
        if "_get_agent_definition_opt_in_keys" in line:
            print("  [Step 1] Global variable already present – skipping")
            return lines

    last_import_idx = -1
    for i, line in enumerate(lines):
        if re.match(r"^(from|import)\b", line):
            last_import_idx = i

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, GLOBAL_VAR_LINE)
        print(f"  [Step 1] Inserted global variable after line {last_import_idx + 1}")
    else:
        print("  [Step 1] WARNING: No import statement found – global variable not inserted")

    return lines


# ---------------------------------------------------------------------------
# Steps 2-5 – state-machine processor
# ---------------------------------------------------------------------------
#
# States:
#   GLOBAL            – scanning at module / top level
#   IN_BUILD          – inside a build_* function (never modified)
#   IN_CLASS_SIG      – inside the signature of a class-level method
#   IN_CLASS_BEFORE_BODY – signature closed; expecting docstring or body start
#   IN_CLASS_DOCSTRING – inside a triple-quoted docstring of a class method
#   IN_CLASS_BODY     – inside the body of a class method implementation
#
# is_overload tracks whether the current method is decorated with @overload.
# For overload methods we remove foundry_features from the signature and
# docstring, but never insert a local variable.
#
# ff_kind / ff_value record what type of foundry_features was found in the
# current method's signature, so we can generate the right local variable.


def steps_2to5(lines):
    """Apply Steps 2-5 to a list of source lines, returning the modified list."""
    result = []
    i = 0

    # --- state ---
    state = "GLOBAL"
    last_decorator = None  # last @xxx decorator seen before a def
    current_indent = ""  # indent of the current method's def line
    current_name = ""  # name of the current method
    is_overload = False  # is the current method an @overload stub?
    ff_kind = None  # type of foundry_features found in signature
    ff_value = None  # enum value (for Literal types) or None
    local_var_inserted = False  # have we inserted _foundry_features yet?
    sig_paren_depth = 0  # open-paren depth within the current signature
    in_keyword_block = False  # inside :keyword foundry_features: doc block

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ---- (A) Decorator lines ----------------------------------------
        if re.match(r"^\s*@\w", line):
            last_decorator = stripped
            result.append(line)
            i += 1
            continue

        # ---- (B) def / async def lines -----------------------------------
        def_m = re.match(r"^( *)(?:async )?def (\w+)\s*\(", line)
        if def_m:
            def_indent = def_m.group(1)
            def_name = def_m.group(2)
            indent_len = len(def_indent)

            # Module-level function (0-indent).  All of these are build_*
            # functions in the sync file; there are none in the aio file.
            if indent_len == 0:
                state = "IN_BUILD"
                current_name = def_name
                current_indent = def_indent
                ff_kind = None
                ff_value = None
                last_decorator = None
                result.append(line)
                i += 1
                sig_paren_depth = line.count("(") - line.count(")")
                continue

            # Class-level method (exactly 4-space indent).
            if indent_len == 4:
                state = "IN_CLASS_SIG"
                is_overload = bool(last_decorator and "overload" in last_decorator)
                ff_kind = None
                ff_value = None
                local_var_inserted = False
                in_keyword_block = False
                current_name = def_name
                current_indent = def_indent
                last_decorator = None
                sig_paren_depth = line.count("(") - line.count(")")
                result.append(line)
                i += 1
                # Handle single-line signatures (rare but possible)
                if sig_paren_depth <= 0:
                    if re.search(r":\s*\.\.\.\s*$", stripped):
                        state = "GLOBAL"
                    else:
                        state = "IN_CLASS_BEFORE_BODY"
                continue

            # Inner function (8+ indent) – must not change state; pass through.
            last_decorator = None
            result.append(line)
            i += 1
            continue

        # ---- (C) Reset last_decorator for non-decorator, non-def lines ---
        if stripped and not stripped.startswith("#"):
            last_decorator = None

        # ================================================================
        #   State-specific processing
        # ================================================================

        # -- GLOBAL / IN_BUILD: pass through unchanged --------------------
        if state in ("GLOBAL", "IN_BUILD"):
            result.append(line)
            i += 1
            continue

        # -- IN_CLASS_SIG: processing the function signature ---------------
        if state == "IN_CLASS_SIG":
            sig_paren_depth += line.count("(") - line.count(")")

            if "foundry_features: " in line:
                ff_kind, ff_value = get_ff_info(line)

                # Is this a STANDALONE foundry_features line?
                # Standalone means the line (after stripping) starts with
                # 'foundry_features: '.
                if re.match(r"^\s*foundry_features:\s+", line):
                    # Delete this line entirely
                    i += 1
                    if sig_paren_depth <= 0:
                        if re.search(r":\s*\.\.\.\s*$", stripped):
                            state = "GLOBAL"
                        else:
                            state = "IN_CLASS_BEFORE_BODY"
                    continue
                else:
                    # COMBINED line – remove the foundry_features fragment.
                    # Pattern: "..., *, foundry_features: TYPE, **kwargs..."
                    # We remove ", *, foundry_features: TYPE," leaving "..., **kwargs..."
                    new_line = re.sub(
                        r",\s*\*,\s*foundry_features:\s+[^,]+(?:=\s*None)?,\s*",
                        ", ",
                        line,
                    )
                    result.append(new_line)
                    i += 1
                    if sig_paren_depth <= 0:
                        if re.search(r":\s*\.\.\.\s*$", new_line.strip()):
                            state = "GLOBAL"
                        else:
                            state = "IN_CLASS_BEFORE_BODY"
                    continue

            result.append(line)
            i += 1
            if sig_paren_depth <= 0:
                if re.search(r":\s*\.\.\.\s*$", stripped):
                    state = "GLOBAL"
                else:
                    state = "IN_CLASS_BEFORE_BODY"
            continue

        # -- IN_CLASS_BEFORE_BODY: looking for docstring or first body line --
        if state == "IN_CLASS_BEFORE_BODY":
            if not stripped:
                # Blank line – keep and stay in this state
                result.append(line)
                i += 1
                continue

            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = '"""' if '"""' in stripped else "'''"
                # Count occurrences to detect single-line docstring
                if stripped.count(quote) >= 2:
                    # Single-line docstring, e.g.  """Retrieves the agent."""
                    result.append(line)
                    i += 1
                    if is_overload:
                        state = "GLOBAL"
                    else:
                        state = "IN_CLASS_BODY"
                        if ff_kind and not local_var_inserted:
                            lv = make_local_var(ff_kind, ff_value, current_indent + "    ")
                            if lv:
                                result.append(lv)
                                local_var_inserted = True
                else:
                    # Start of multi-line docstring
                    state = "IN_CLASS_DOCSTRING"
                    in_keyword_block = False
                    result.append(line)
                    i += 1
                continue

            if stripped == "...":
                # Overload stub body on its own line (no docstring)
                result.append(line)
                i += 1
                state = "GLOBAL"
                continue

            # First real body line (no docstring)
            state = "IN_CLASS_BODY"
            if not is_overload and ff_kind and not local_var_inserted:
                lv = make_local_var(ff_kind, ff_value, current_indent + "    ")
                if lv:
                    result.append(lv)
                    local_var_inserted = True
            result.append(line)
            i += 1
            continue

        # -- IN_CLASS_DOCSTRING: inside the triple-quoted docstring ----------
        if state == "IN_CLASS_DOCSTRING":
            # Handle :keyword foundry_features: removal
            if ":keyword foundry_features:" in line:
                in_keyword_block = True
                i += 1  # skip this line
                continue

            if in_keyword_block:
                if ":paramtype foundry_features:" in line:
                    # End of the foundry_features docstring block; skip this line
                    in_keyword_block = False
                    i += 1
                    continue
                if stripped.startswith(":"):
                    # A new :keyword/:paramtype/:param/:return/etc. section
                    in_keyword_block = False
                    result.append(line)
                    i += 1
                    continue
                # Continuation of the foundry_features description – skip
                i += 1
                continue

            # Detect end of docstring (closing triple-quote)
            if '"""' in stripped or "'''" in stripped:
                # Check it's not just an opening quote (it IS the closing)
                result.append(line)
                i += 1
                if is_overload:
                    # Overload: the docstring IS the body – method is done
                    state = "GLOBAL"
                else:
                    # Implementation: body follows
                    state = "IN_CLASS_BODY"
                    if ff_kind and not local_var_inserted:
                        lv = make_local_var(ff_kind, ff_value, current_indent + "    ")
                        if lv:
                            result.append(lv)
                            local_var_inserted = True
                continue

            result.append(line)
            i += 1
            continue

        # -- IN_CLASS_BODY: inside the method implementation body ------------
        if state == "IN_CLASS_BODY":
            # Step 4: replace foundry_features=foundry_features in build_ calls
            if "foundry_features=foundry_features" in line:
                line = line.replace(
                    "foundry_features=foundry_features",
                    "foundry_features=_foundry_features",
                )

            # Step 5: add Foundry-Features header in prepare_request GET calls
            # Only applicable when this method had foundry_features.
            get_str = '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path),' " params=_next_request_params"
            if ff_kind is not None and get_str in line and "Foundry-Features" not in line:
                new_get = (
                    '"GET", urllib.parse.urljoin(next_link, _parsed_next_link.path),'
                    " params=_next_request_params,"
                    ' headers={"Foundry-Features":'
                    ' _SERIALIZER.header("foundry_features", _foundry_features, "str")}'
                )
                line = line.replace(get_str, new_get)

            result.append(line)
            i += 1
            continue

        # Fallback (should not be reached)
        result.append(line)
        i += 1

    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def process_file(filepath):
    print(f"\nProcessing: {filepath}")
    if not os.path.isfile(filepath):
        print(f"  ERROR: File not found – {filepath}")
        return False

    with open(filepath, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    print(f"  Original line count: {len(lines)}")

    lines = step1_insert_global(lines)
    lines = steps_2to5(lines)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    print(f"  Modified line count: {len(lines)}")
    return True


def main():
    # Ensure we're running from the correct directory
    for filepath in FILES:
        if not os.path.isfile(filepath):
            print(
                f"ERROR: Expected to run from the azure-ai-projects folder, "
                f"but '{filepath}' was not found.\n"
                f"Please run this script from:\n"
                f"  \\azure-sdk-for-python\\sdk\\ai\\azure-ai-projects"
            )
            sys.exit(1)

    success = True
    for filepath in FILES:
        ok = process_file(filepath)
        success = success and ok

    if success:
        print("\nAll files processed successfully.")
    else:
        print("\nOne or more files could not be processed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
