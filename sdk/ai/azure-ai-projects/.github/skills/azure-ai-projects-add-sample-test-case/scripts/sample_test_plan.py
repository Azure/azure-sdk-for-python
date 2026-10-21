# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Read-only, standard-library planner for AddSampleTestCase.ps1."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        return call_name(node.func)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


@dataclass
class Source:
    path: Path
    before: str | None
    text: str
    bom: bool = False

    @classmethod
    def read(cls, path: Path) -> Source:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        return cls(path, text, text, raw.startswith(b"\xef\xbb\xbf"))

    @property
    def newline(self) -> str:
        return "\r\n" if "\r\n" in self.text else "\n"

    def span(self, node: ast.expr | ast.stmt) -> tuple[int, int]:
        # AST columns are UTF-8 byte offsets, not Python string offsets.
        lines = self.text.splitlines(keepends=True)

        def offset(line: int, column: int) -> int:
            prefix = lines[line - 1].encode("utf-8")[:column].decode("utf-8")
            return sum(map(len, lines[: line - 1])) + len(prefix)

        if node.end_lineno is None or node.end_col_offset is None:
            raise ValueError(f"Missing AST source location in {self.path}.")
        return offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)

    def replace(self, start: int, end: int, replacement: str) -> None:
        self.text = self.text[:start] + replacement + self.text[end:]


@dataclass
class Registration:
    source: Source
    function: ast.FunctionDef | ast.AsyncFunctionDef
    qualifier: str
    decorator_index: int
    call: ast.Call
    folder: str
    is_async: bool

    def selection(self) -> tuple[str, ast.List, list[str]]:
        options = [
            item
            for item in self.call.keywords
            if item.arg in ("samples_to_test", "samples_to_skip")
            and not (isinstance(item.value, ast.Constant) and item.value.value is None)
        ]
        if len(options) != 1:
            raise ValueError(f"Expected one literal include/exclude list in {self.qualifier} ({self.source.path}).")
        option = options[0]
        if option.arg is None or not isinstance(option.value, ast.List):
            raise ValueError(f"Expected one literal include/exclude list in {self.qualifier} ({self.source.path}).")
        names = ast.literal_eval(option.value)
        if not all(isinstance(name, str) for name in names):
            raise ValueError(f"Non-string sample list in {self.qualifier}.")
        return option.arg, option.value, names

    def node_id(self, root: Path, test_id: str) -> str:
        return f"{self.source.path.relative_to(root).as_posix()}::{self.qualifier}[{test_id}]"

    def ids_for(self, filename: str) -> list[str]:
        mode, _, names = self.selection()
        included = (
            filename in names
            if mode == "samples_to_test"
            else (filename not in names and filename.endswith("_async.py") == self.is_async)
        )
        ids = [filename[:-3]] if included else []
        # Only active decorators above parametrize can expand its test IDs.
        for decorator in self.function.decorator_list[: self.decorator_index]:
            if call_name(decorator) != "additionalSampleTests":
                continue
            for node in ast.walk(decorator):
                if not isinstance(node, ast.Call) or call_name(node) != "AdditionalSampleTestDetail":
                    continue
                values = {item.arg: item.value for item in node.keywords}
                sample = ast.literal_eval(values["sample_filename"])
                if Path(sample.replace("\\", "/")).name != filename:
                    continue
                test_id = ast.literal_eval(values["test_id"]) if "test_id" in values else None
                if test_id is None:
                    env = values["env_vars"]
                    if not isinstance(env, ast.Dict) or any(key is None for key in env.keys):
                        raise ValueError(f"Cannot resolve dynamic variant ID in {self.qualifier}.")
                    keys = sorted(ast.literal_eval(key) for key in env.keys if key is not None)
                    test_id = f"{filename[:-3]}-[{','.join(keys)}]"
                if not isinstance(test_id, str):
                    raise ValueError(f"Expected a string variant ID in {self.qualifier}.")
                ids.append(test_id)
        return ids


def registrations(sources: dict[Path, Source]) -> list[Registration]:
    found = []
    for source in sources.values():
        tree = ast.parse(source.text, filename=str(source.path))
        containers = [("", tree)] + [(f"{node.name}::", node) for node in tree.body if isinstance(node, ast.ClassDef)]
        for prefix, container in containers:
            for function in container.body:
                if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) or not function.name.startswith(
                    "test_"
                ):
                    continue
                for index, decorator in enumerate(function.decorator_list):
                    if not isinstance(decorator, ast.Call) or call_name(decorator) != "parametrize":
                        continue
                    if len(decorator.args) < 2 or not isinstance(decorator.args[0], ast.Constant):
                        continue
                    if decorator.args[0].value != "sample_path":
                        continue
                    call = decorator.args[1]
                    if not isinstance(call, ast.Call) or call_name(call) not in (
                        "get_sample_paths",
                        "get_async_sample_paths",
                    ):
                        continue
                    if (
                        not call.args
                        or not isinstance(call.args[0], ast.Constant)
                        or not isinstance(call.args[0].value, str)
                    ):
                        raise ValueError(f"Dynamic sample folder in {source.path}: {function.name}.")
                    folder = call.args[0].value.replace("\\", "/").strip("/")
                    found.append(
                        Registration(
                            source,
                            function,
                            prefix + function.name,
                            index,
                            call,
                            "" if folder == "." else folder,
                            call_name(call) == "get_async_sample_paths",
                        )
                    )
    return found


def update_list(source: Source, node: ast.List, filename: str, *, remove: bool) -> None:
    start, end = source.span(node)
    segment = source.text[start:end]
    if remove:
        # Reparse after each removal so even duplicate exclusions are handled.
        while True:
            current = Source(source.path, segment, segment)
            expression = ast.parse(segment, mode="eval").body
            if not isinstance(expression, ast.List):
                raise ValueError(f"Expected a sample list in {source.path}.")
            items = expression.elts
            matches = [i for i, item in enumerate(items) if ast.literal_eval(item) == filename]
            if not matches:
                break
            index = matches[-1]
            left, right = current.span(items[index])
            line_start = segment.rfind("\n", 0, left) + 1
            line_end = segment.find("\n", right)
            line_end = len(segment) if line_end < 0 else line_end + 1
            if not segment[line_start:left].strip() and re.fullmatch(
                r"[ \t]*,?[ \t]*(?:#[^\r\n]*)?\r?\n?", segment[right:line_end]
            ):
                left, right = line_start, line_end
            else:
                comma = re.match(r"[ \t]*,[ \t]*", segment[right:])
                if comma:
                    right += comma.end()
                elif index:
                    previous_end = current.span(items[index - 1])[1]
                    gap = segment[previous_end:left]
                    if not re.fullmatch(r"\s*,\s*", gap):
                        raise ValueError(f"Cannot safely remove inline exclusion in {source.path}.")
                    left = previous_end
            segment = segment[:left] + segment[right:]
    else:
        items = node.elts
        literal = json.dumps(filename)
        close_line = segment.rfind("\n") + 1
        if "\n" in segment and not segment[close_line:-1].strip():
            insertion = segment[close_line:-1] + "    " + literal + "," + source.newline
            if items:
                last_end = source.span(items[-1])[1] - start
                if not re.match(r"\s*,", segment[last_end:-1]):
                    segment = segment[:last_end] + "," + segment[last_end:]
                    close_line += 1
            segment = segment[:close_line] + insertion + segment[close_line:]
        else:
            prefix = segment[:-1].rstrip(" \t")
            separator = " " if prefix.endswith(",") else ", "
            segment = prefix + (separator if items else "") + literal + segment[len(prefix) :]
    ast.parse(segment, mode="eval")
    source.replace(start, end, segment)


def add_folder_test(sources: dict[Path, Source], root: Path, folder: str, filename: str) -> None:
    is_async = filename.endswith("_async.py")
    path = root / "tests" / "samples" / ("test_samples_async.py" if is_async else "test_samples.py")
    class_name = "TestSamplesAsync" if is_async else "TestSamples"
    executor = "AsyncSampleExecutor" if is_async else "SyncSampleExecutor"
    discover = "get_async_sample_paths" if is_async else "get_sample_paths"
    recorded = "recorded_by_proxy_async" if is_async else "recorded_by_proxy"
    imports = [
        ("pytest", ["pytest"]),
        ("devtools_testutils", ["AzureRecordedTestCase", "RecordedTransport"]),
        ("devtools_testutils.aio" if is_async else "devtools_testutils", [recorded]),
        ("test_base", ["servicePreparer"]),
        ("sample_executor", [executor, "SamplePathPasser", discover]),
        ("test_samples_helpers", ["get_sample_env_vars"]),
    ]
    if path not in sources:
        text = (
            "# Copyright (c) Microsoft Corporation.\n# Licensed under the MIT License.\n\n"
            f'class {class_name}(AzureRecordedTestCase):\n    """Recorded sample tests."""\n'
        )
        sources[path] = Source(path, None, text)
    source = sources[path]
    tree = ast.parse(source.text)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        raise ValueError(f"Expected one {class_name} class in {path}.")
    target = classes[0]
    bound = {
        alias.asname or alias.name
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    missing = []
    for module, names in imports:
        names = [name for name in names if name not in bound]
        if names:
            missing.append("import pytest" if module == "pytest" else f"from {module} import {', '.join(names)}")
    if missing:
        insertion = sum(map(len, source.text.splitlines(keepends=True)[: target.lineno - 1]))
        source.replace(insertion, insertion, source.newline.join(missing) + source.newline * 2)
        target = next(
            node for node in ast.parse(source.text).body if isinstance(node, ast.ClassDef) and node.name == class_name
        )

    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", folder).strip("_") or "root"
    base = f"test_{slug}_samples" + ("_async" if is_async else "")
    existing = {node.name for node in target.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    name = base
    suffix = 2
    while name in existing:
        name = f"{base}_{suffix}"
        suffix += 1
    declaration = "async def" if is_async else "def"
    execute = "await executor.execute_async()" if is_async else "executor.execute()"
    validate = (
        "await executor.validate_print_calls_by_llm_async()" if is_async else "executor.validate_print_calls_by_llm()"
    )
    method = f"""
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        {discover}(
            {json.dumps(folder)},
            samples_to_test=[
                {json.dumps(filename)},
            ],
        ),
    )
    @SamplePathPasser()
    @{recorded}(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    {declaration} {name}(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = {executor}(self, sample_path, env_vars=env_vars, **kwargs)
        {execute}
        {validate}
    """.rstrip().replace("\n", source.newline) + source.newline
    insertion = sum(map(len, source.text.splitlines(keepends=True)[: target.end_lineno]))
    prefix = "" if source.text[:insertion].endswith("\n") else source.newline
    source.replace(insertion, insertion, prefix + method)


def resolve_samples(root: Path, requests: list[str]) -> list[Path]:
    samples_root = (root / "samples").resolve()
    resolved = []
    for request in requests:
        path = Path(request.replace("\\", "/"))
        candidates = [path] if path.is_absolute() else [root / path, samples_root / path]
        matches = {candidate.resolve() for candidate in candidates if candidate.is_file()}
        if not matches and len(path.parts) == 1:
            matches = {candidate.resolve() for candidate in samples_root.rglob(path.name) if candidate.is_file()}
        if len(matches) != 1:
            raise ValueError(f"Sample '{request}' is missing or ambiguous; pass an exact sample path.")
        sample = matches.pop()
        if not sample.is_relative_to(samples_root) or not sample.name.startswith("sample_") or sample.suffix != ".py":
            raise ValueError(f"Not a sample_*.py file under {samples_root}: {request}")
        if sample not in resolved:
            resolved.append(sample)
    return resolved


def build_plan(root: Path, requests: list[str]) -> dict:
    root = root.resolve()
    if not (root / "tests" / "samples").is_dir() or not (root / "samples").is_dir():
        raise ValueError(f"Not an azure-ai-projects package root: {root}")
    samples = resolve_samples(root, requests)
    sources = {path: Source.read(path) for path in sorted((root / "tests" / "samples").glob("test_sample*.py"))}
    results = []
    for sample in samples:
        folder = sample.parent.relative_to(root / "samples").as_posix()
        folder = "" if folder == "." else folder
        groups = [item for item in registrations(sources) if item.folder == folder]
        node_ids = [item.node_id(root, test_id) for item in groups for test_id in item.ids_for(sample.name)]
        action = "already-registered"
        if not node_ids:
            candidates = [item for item in groups if item.is_async == sample.name.endswith("_async.py")]
            exclusions = [item for item in candidates if item.selection()[0] == "samples_to_skip"]
            candidates = exclusions or candidates
            if len(candidates) > 1:
                raise ValueError(
                    f"Multiple folder tests could register {sample.relative_to(root)}; select the test manually."
                )
            if candidates:
                target = candidates[0]
                mode, values, _ = target.selection()
                update_list(target.source, values, sample.name, remove=mode == "samples_to_skip")
                action = "exclude-removed" if mode == "samples_to_skip" else "include-added"
            else:
                add_folder_test(sources, root, folder, sample.name)
                action = "folder-test-created"
            node_ids = [
                item.node_id(root, test_id)
                for item in registrations(sources)
                if item.folder == folder
                for test_id in item.ids_for(sample.name)
            ]
            if not node_ids:
                raise ValueError(f"Failed to register {sample.relative_to(root)}.")
        results.append(
            {"samplePath": sample.relative_to(root).as_posix(), "action": action, "nodeIds": sorted(set(node_ids))}
        )

    files = []
    for source in sources.values():
        if source.text != source.before:
            ast.parse(source.text, filename=str(source.path))
            files.append(
                {
                    "path": str(source.path),
                    "relativePath": source.path.relative_to(root).as_posix(),
                    "before": source.before,
                    "after": source.text,
                    "bom": source.bom,
                }
            )
    return {"samples": results, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("samples", nargs="+")
    arguments = parser.parse_args()
    try:
        plan = build_plan(arguments.package_root, arguments.samples)
    except (OSError, SyntaxError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Cannot plan sample registration: {error}\n")
    print(json.dumps(plan))


if __name__ == "__main__":
    main()
