# pylint: disable=line-too-long,useless-suppression
#!/usr/bin/env python3
"""
Patch script to modify foundry_features arguments in operations files.

This script:
1. Finds all public methods with required 'foundry_features' input arguments
2. Removes the argument from method signatures and docstrings
3. Adds an assignment at the start of the method body
4. Skips internal helper methods with names starting with 'build_beta_'
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Files to process
FILES_TO_PROCESS = [
    r"azure\ai\projects\aio\operations\_operations.py",
    r"azure\ai\projects\operations\_operations.py",
]


def is_decorated_method(lines: List[str], line_idx: int) -> Tuple[bool, Optional[str]]:
    """
    Check if the current line is preceded by a relevant decorator.
    Returns (is_decorated, decorator_name).
    """
    # Look back for decorator
    for i in range(line_idx - 1, max(0, line_idx - 10), -1):
        stripped = lines[i].strip()
        if stripped.startswith("@distributed_trace_async"):
            return True, "distributed_trace_async"
        elif stripped.startswith("@distributed_trace") and not "async" in stripped:
            return True, "distributed_trace"
        elif stripped.startswith("@overload"):
            return True, "overload"
        elif stripped.startswith("def ") or stripped.startswith("async def ") or stripped.startswith("class "):
            break
        elif stripped == "" or stripped.startswith("#"):
            continue
    return False, None


def extract_foundry_value(signature: str) -> Optional[str]:
    """Extract the FoundryFeaturesOptInKeys value from a signature."""
    match = re.search(r"foundry_features:\s*Literal\[FoundryFeaturesOptInKeys\.(\w+)\]", signature)
    if match:
        return match.group(1)
    return None


def has_optional_foundry_features(signature: str) -> bool:
    """Check if foundry_features is Optional in the signature."""
    return bool(re.search(r"foundry_features:\s*Optional\[", signature))


def remove_foundry_features_from_lines(sig_lines: List[str]) -> List[str]:
    """
    Remove the foundry_features parameter from signature lines.
    Returns the modified lines.
    """
    # Join lines for easier pattern matching, preserving structure
    signature = "\n".join(sig_lines)

    # Pattern: line with foundry_features: Literal[FoundryFeaturesOptInKeys.XXX]
    # We need to handle:
    # 1. Single line: "self, name: str, *, foundry_features: Literal[...], **kwargs: Any"
    # 2. Multi-line: foundry_features on its own line

    new_lines = []
    skip_star_comma = False

    for i, line in enumerate(sig_lines):
        # Check if this line contains the foundry_features definition
        if "foundry_features:" in line and "Literal[FoundryFeaturesOptInKeys." in line:
            # This is the line to remove or modify

            # Check if it's part of a single-line signature
            if ", *," in line and "**kwargs" in line:
                # Pattern: "self, name: str, *, foundry_features: Literal[...], **kwargs: Any"
                # Replace with: "self, name: str, **kwargs: Any"
                new_line = re.sub(
                    r",\s*\*\s*,\s*foundry_features:\s*Literal\[FoundryFeaturesOptInKeys\.\w+\]\s*,\s*", ", ", line
                )
                new_lines.append(new_line)
            elif line.strip().startswith("foundry_features:"):
                # foundry_features is on its own line
                # Check if previous line was just "*,"
                if new_lines and new_lines[-1].strip() == "*,":
                    # Check if there are more params after this
                    has_more_params = False
                    for j in range(i + 1, len(sig_lines)):
                        rest = sig_lines[j].strip()
                        if rest and not rest.startswith(")") and not rest.startswith("**kwargs"):
                            has_more_params = True
                            break

                    if not has_more_params:
                        # Remove the *, line too
                        new_lines.pop()
                # Skip this foundry_features line entirely
                continue
            else:
                # foundry_features embedded in a line with other params
                # Remove just the foundry_features part
                new_line = re.sub(r",?\s*foundry_features:\s*Literal\[FoundryFeaturesOptInKeys\.\w+\]\s*,?", "", line)
                # Clean up resulting issues
                new_line = re.sub(r",\s*,", ",", new_line)
                new_line = re.sub(r",\s*\)", ")", new_line)
                new_line = re.sub(r"\(\s*,", "(", new_line)
                if new_line.strip():
                    new_lines.append(new_line)
                continue
        else:
            new_lines.append(line)

    # Clean up: if we have "*, " at end of a line followed by "**kwargs", merge nicely
    result = "\n".join(new_lines)
    # Remove empty *, line followed by **kwargs
    result = re.sub(r"\n\s*\*\s*,\s*\n(\s*\*\*kwargs)", r"\n\1", result)

    return result.split("\n")


def remove_foundry_features_from_docstring_lines(doc_lines: List[str]) -> List[str]:
    """Remove foundry_features documentation from docstring lines."""
    new_lines = []
    skip_continuation = False

    for line in doc_lines:
        # Check for :keyword foundry_features:
        if ":keyword foundry_features:" in line:
            skip_continuation = True
            continue

        # Check for :paramtype foundry_features:
        if ":paramtype foundry_features:" in line:
            continue

        # Check if this is a continuation line for foundry_features
        if skip_continuation:
            stripped = line.strip()
            if stripped.startswith(":") or stripped.startswith('"""') or not stripped:
                skip_continuation = False
            else:
                continue

        new_lines.append(line)

    return new_lines


def process_file(filepath: str) -> List[Dict]:
    """Process a single file to patch foundry_features arguments."""

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Convert to list without newlines for easier processing
    lines = [line.rstrip("\n") for line in lines]
    original_lines = lines.copy()

    modified_methods = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for decorated method start
        if stripped.startswith(("@distributed_trace", "@overload")):
            decorator = None
            if "@distributed_trace_async" in stripped:
                decorator = "distributed_trace_async"
            elif "@distributed_trace" in stripped:
                decorator = "distributed_trace"
            elif "@overload" in stripped:
                decorator = "overload"

            decorator_idx = i

            # Find the def line
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("def ", "async def ")):
                i += 1

            if i >= len(lines):
                continue

            def_idx = i
            def_line = lines[i]

            # Extract method name
            method_match = re.match(r"\s*(async\s+)?def\s+(\w+)", def_line)
            if not method_match:
                i += 1
                continue

            method_name = method_match.group(2)

            # Skip build_ functions
            if method_name.startswith("build_"):
                i += 1
                continue

            # Collect the full signature (may span multiple lines)
            sig_start = i
            paren_count = def_line.count("(") - def_line.count(")")
            i += 1

            while paren_count > 0 and i < len(lines):
                paren_count += lines[i].count("(") - lines[i].count(")")
                i += 1

            sig_end = i - 1
            sig_lines = lines[sig_start : sig_end + 1]
            signature = "\n".join(sig_lines)

            # Check if this has required foundry_features
            foundry_value = extract_foundry_value(signature)
            if not foundry_value or has_optional_foundry_features(signature):
                continue

            # Remove foundry_features from signature
            new_sig_lines = remove_foundry_features_from_lines(sig_lines)

            # Replace signature in lines
            lines = lines[:sig_start] + new_sig_lines + lines[sig_end + 1 :]

            # Adjust i to account for potential line count change
            new_sig_end = sig_start + len(new_sig_lines) - 1
            i = new_sig_end + 1

            # Find and process docstring for ALL methods (including overloads)
            doc_start = None
            doc_end = None

            for idx in range(i, min(i + 5, len(lines))):
                if '"""' in lines[idx]:
                    doc_start = idx
                    if lines[idx].count('"""') >= 2:
                        doc_end = idx
                    else:
                        for end_idx in range(idx + 1, len(lines)):
                            if '"""' in lines[end_idx]:
                                doc_end = end_idx
                                break
                    break

            if doc_start is not None and doc_end is not None:
                # Remove foundry_features from docstring
                doc_lines = lines[doc_start : doc_end + 1]
                new_doc_lines = remove_foundry_features_from_docstring_lines(doc_lines)

                # Replace docstring
                lines = lines[:doc_start] + new_doc_lines + lines[doc_end + 1 :]
                doc_end = doc_start + len(new_doc_lines) - 1

            # For main methods (not overloads), add assignment after docstring
            if decorator != "overload":
                if doc_end is not None:
                    insert_idx = doc_end + 1

                    # Determine indentation
                    if insert_idx < len(lines):
                        next_line = lines[insert_idx]
                        indent_match = re.match(r"^(\s+)", next_line)
                        indent = indent_match.group(1) if indent_match else "        "
                    else:
                        indent = "        "

                    # Insert the assignment with type annotation for mypy compatibility
                    assignment = f"{indent}foundry_features: Literal[FoundryFeaturesOptInKeys.{foundry_value}] = FoundryFeaturesOptInKeys.{foundry_value}"
                    lines.insert(insert_idx, assignment)
                    i = insert_idx + 1

                # Track this method
                if not any(
                    m["method_name"] == method_name and m["foundry_value"] == foundry_value for m in modified_methods
                ):
                    modified_methods.append(
                        {
                            "method_name": method_name,
                            "foundry_value": foundry_value,
                            "file": filepath,
                        }
                    )

            continue

        i += 1

    # Write back if changed
    if lines != original_lines:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return modified_methods


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent

    all_modified = []

    for rel_path in FILES_TO_PROCESS:
        filepath = script_dir / rel_path
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue

        print(f"\nProcessing: {filepath}")

        modified = process_file(str(filepath))
        all_modified.extend(modified)

        print(f"  Modified {len(modified)} methods")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)

    if not all_modified:
        print("No methods were modified.")
    else:
        # Group by file
        by_file = {}
        for m in all_modified:
            fname = Path(m["file"]).name
            if fname not in by_file:
                by_file[fname] = []
            by_file[fname].append(m)

        for fname, methods in by_file.items():
            print(f"\n{fname}:")
            print("-" * 40)

            # Group by foundry value
            by_value = {}
            for m in methods:
                v = m["foundry_value"]
                if v not in by_value:
                    by_value[v] = []
                by_value[v].append(m["method_name"])

            for value, method_names in sorted(by_value.items()):
                print(f"\n  FoundryFeaturesOptInKeys.{value}:")
                for name in sorted(set(method_names)):
                    print(f"    - {name}")

        print(f"\nTotal methods modified: {len(all_modified)}")


if __name__ == "__main__":
    main()
