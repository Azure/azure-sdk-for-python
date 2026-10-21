# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Plan missing template entries and servicePreparer defaults without reading .env."""

from __future__ import annotations

import argparse
import ast
import json
import keyword
from pathlib import Path
import re
import sys

from sample_test_plan import Source

ZERO_UUID = "00000000-0000-0000-0000-000000000000"
PROJECT_ENDPOINT = "https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name"
PROJECT_RESOURCE_ID = (
    f"/subscriptions/{ZERO_UUID}/resourceGroups/sanitized-resource-group"
    "/providers/Microsoft.CognitiveServices/accounts/sanitized-account/projects/sanitized-project"
)
# These are loader options, not environment-variable defaults.
LOADER_OPTIONS = {
    "directory",
    "name_prefix",
    "disable_recording",
    "client_kwargs",
    "random_name_enabled",
    "use_cache",
    "preparers",
    "options",
}


def sanitized_default(name: str) -> str:
    """Use deterministic placeholders; never derive a default from live configuration."""
    slug = name.lower().replace("_", "-")
    if name == "USER_INPUT" or name.endswith("_USER_INPUT"):
        return f"What is {slug.replace('-', ' ')}?"
    if name.endswith(("_PROJECT_ENDPOINT", "_PROJECTS_ENDPOINT")):
        return PROJECT_ENDPOINT
    if name.endswith("_PROJECT_CONNECTION_ID"):
        connection = name[: -len("_PROJECT_CONNECTION_ID")].lower().replace("_", "-")
        return f"{PROJECT_RESOURCE_ID}/connections/sanitized-{connection}-connection"
    if name.endswith(
        ("_SUBSCRIPTION_ID", "_TENANT_ID", "_CLIENT_ID", "_APP_ID", "_OBJECT_ID", "_PRINCIPAL_ID", "_UUID", "_GUID")
    ):
        return ZERO_UUID
    if name.endswith(("_ENDPOINT", "_URL", "_URI")):
        return f"https://sanitized-{slug}.example.com"
    if name.endswith(("_VERSION", "_SECONDS", "_HOURS", "_DAYS", "_COUNT", "_LIMIT", "_SIZE", "_PORT")):
        return "1"
    return f"sanitized-{slug}"


def service_preparer_call(source: Source) -> ast.Call:
    calls = []
    for node in ast.parse(source.text, filename=str(source.path)).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "servicePreparer" for target in node.targets
        ):
            calls.append(node.value)
    if len(calls) != 1 or not isinstance(calls[0], ast.Call):
        raise ValueError(f"Expected one servicePreparer assignment in {source.path}.")
    call = calls[0]
    function = call.func
    name = function.id if isinstance(function, ast.Name) else getattr(function, "attr", None)
    if (
        name != "partial"
        or len(call.args) != 2
        or not isinstance(call.args[0], ast.Name)
        or call.args[0].id != "EnvironmentVariableLoader"
        or not isinstance(call.args[1], ast.Constant)
        or call.args[1].value != ""
        or any(item.arg is None for item in call.keywords)
    ):
        raise ValueError(
            "Expected servicePreparer = functools.partial(EnvironmentVariableLoader, '', literal keywords)."
        )
    names = [item.arg.lower() for item in call.keywords if item.arg is not None]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate environment-variable keywords in servicePreparer.")
    return call


def append_preparer_defaults(source: Source, call: ast.Call, additions: dict[str, str]) -> None:
    if not additions:
        return
    _, end = source.span(call)
    close = end - 1
    line_start = source.text.rfind("\n", 0, close) + 1
    arguments = [*call.args, *(item.value for item in call.keywords)]
    last = max(arguments, key=lambda node: (node.lineno, node.col_offset))
    _, last_end = source.span(last)
    if source.text[line_start:close].strip():
        # Keep compact preparers compact, including their existing trailing comma.
        prefix = source.text[:close].rstrip(" \t")
        separator = " " if prefix.endswith(",") else ", "
        text = ", ".join(f"{name}={json.dumps(value)}" for name, value in additions.items())
        source.replace(len(prefix), close, separator + text)
    else:
        indent = source.text[line_start:close] + "    "
        if not re.match(r"\s*,", source.text[last_end:close]):
            source.replace(last_end, last_end, ",")
            line_start += 1
        text = "".join(f"{indent}{name}={json.dumps(value)},{source.newline}" for name, value in additions.items())
        source.replace(line_start, line_start, text)
    # Compile checks duplicate keywords as well as syntax, without executing anything.
    compile(source.text, str(source.path), "exec")


def build_environment_plan(root: Path, names: list[str], sanitized_values: dict[str, str] | None = None) -> dict:
    root = root.resolve()
    if not isinstance(names, list) or not all(
        isinstance(name, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", name) for name in names
    ):
        raise ValueError("Required environment names must be uppercase identifiers.")
    names = sorted(set(names))
    overrides = {} if sanitized_values is None else sanitized_values
    if not isinstance(overrides, dict) or any(
        name not in names or not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value
        for name, value in overrides.items()
    ):
        raise ValueError(
            "SanitizedValue must map scanned names to nonempty, single-line playback strings, never secrets."
        )
    for name in names:
        if keyword.iskeyword(name.lower()) or name.lower() in LOADER_OPTIONS:
            raise ValueError(f"Cannot use {name} as an EnvironmentVariableLoader keyword.")

    environment = {"requiredNames": names, "templateAdded": [], "servicePreparerAdded": []}
    if not names:
        return {"environment": environment, "files": []}

    # Read only these two checked-in files; do not load dotenv or the process environment.
    template = Source.read(root / ".env.template")
    preparer = Source.read(root / "tests" / "test_base.py")
    call = service_preparer_call(preparer)
    existing_defaults = {item.arg.lower() for item in call.keywords if item.arg is not None}
    existing_names = set(re.findall(r"(?m)^[ \t]*(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=", template.text))
    missing_names = [name for name in names if name not in existing_names]
    if missing_names:
        separator = "" if not template.text or template.text.endswith("\n") else template.newline
        template.text += separator + template.newline + "# Required by registered sample tests" + template.newline
        template.text += "".join(f"{name}={template.newline}" for name in missing_names)
        environment["templateAdded"] = missing_names

    additions = {
        name.lower(): overrides.get(name, sanitized_default(name))
        for name in names
        if name.lower() not in existing_defaults
    }
    append_preparer_defaults(preparer, call, additions)
    environment["servicePreparerAdded"] = [
        {"name": name.upper(), "keyword": name, "value": value} for name, value in additions.items()
    ]
    files = [
        {
            "path": str(source.path),
            "relativePath": source.path.relative_to(root).as_posix(),
            "before": source.before,
            "after": source.text,
            "bom": source.bom,
        }
        for source in (template, preparer)
        if source.text != source.before
    ]
    return {"environment": environment, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        plan = build_environment_plan(arguments.package_root, data["names"], data.get("sanitizedValues"))
    except (OSError, SyntaxError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, f"Cannot plan sample environment: {error}\n")
    print(json.dumps(plan))


if __name__ == "__main__":
    main()
