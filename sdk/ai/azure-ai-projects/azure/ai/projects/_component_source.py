# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Snapshot source files for Python-backed pipeline components."""

import inspect
import keyword
import os
import shutil
import stat
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Callable, List, Tuple, Union

from pathspec import GitIgnoreSpec

_RUNNER_NAME = "__foundry_component_runner__.py"
_IGNORE_FILES = (".amlignore", ".gitignore")
_EXCLUDED_DIRECTORIES = frozenset((".git", ".venv", "__pycache__"))


def _is_link(path: Path) -> bool:
    """Detect symlinks and Windows junctions before copying any source files."""
    return path.is_symlink() or (
        os.name == "nt" and bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    )


@dataclass(frozen=True)
class _ComponentSource:
    root: Path
    relative_file: Path
    module: str


def _source_for_component(func: Callable[..., object], code: Union[str, PathLike[str]]) -> _ComponentSource:
    source_name = inspect.getsourcefile(func)
    if source_name is None:
        raise ValueError(f"Component '{func.__name__}' must be defined in a readable Python source file.")
    source_file = Path(source_name).resolve()
    if not source_file.is_file() or source_file.suffix != ".py":
        raise ValueError(f"Component '{func.__name__}' must be defined in a readable Python source file.")

    root = Path(code)
    if not root.is_absolute():
        root = source_file.parent / root
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Component '{func.__name__}' code root '{root}' must be an existing directory.")
    try:
        relative_file = source_file.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Component '{func.__name__}' source file must be inside its code root '{root}'.") from error

    if func.__qualname__ != func.__name__:
        raise ValueError(f"Source-backed component '{func.__name__}' must be a module-level function.")
    free_vars = inspect.getclosurevars(func)
    if free_vars.nonlocals:
        raise ValueError(
            f"Component '{func.__name__}' cannot capture enclosing variables: {sorted(free_vars.nonlocals)}."
        )

    module_path = relative_file.parent if relative_file.name == "__init__.py" else relative_file.with_suffix("")
    if not module_path.parts or any(not part.isidentifier() or keyword.iskeyword(part) for part in module_path.parts):
        raise ValueError(f"Component '{func.__name__}' needs an importable Python module under its code root.")
    return _ComponentSource(root=root, relative_file=relative_file, module=".".join(module_path.parts))


def _is_ignored(relative_path: Path, is_directory: bool, rules: List[Tuple[Path, GitIgnoreSpec]]) -> bool:
    ignored = False
    for directory, spec in rules:
        path_from_ignore = relative_path.relative_to(directory).as_posix()
        result = spec.check_file(path_from_ignore + ("/" if is_directory else ""))
        if result.include is not None:
            ignored = result.include
    return ignored


def _copy_source_tree(
    source: Path, destination: Path, code_root: Path, rules: List[Tuple[Path, GitIgnoreSpec]]
) -> None:
    ignore_path = next((source / name for name in _IGNORE_FILES if (source / name).exists()), None)
    if ignore_path is not None:
        if _is_link(ignore_path) or not ignore_path.is_file():
            raise ValueError(f"Code ignore file '{ignore_path}' must be a regular file.")
        relative_directory = source.relative_to(code_root)
        rules = [
            *rules,
            (relative_directory, GitIgnoreSpec.from_lines(ignore_path.read_text(encoding="utf-8").splitlines())),
        ]

    for path in sorted(source.iterdir()):
        if path.name in _IGNORE_FILES:
            continue
        relative_path = path.relative_to(code_root)
        is_directory = path.is_dir()
        if (
            path.name in _EXCLUDED_DIRECTORIES
            or path.name == ".env"
            or path.name.startswith(".env.")
            or path.suffix == ".pyc"
            or _is_ignored(relative_path, is_directory, rules)
        ):
            continue
        if _is_link(path):
            raise ValueError(f"Code root '{code_root}' contains an included link or junction: '{relative_path}'.")
        target = destination / path.name
        if is_directory:
            target.mkdir()
            _copy_source_tree(path, target, code_root, rules)
        elif path.is_file():
            shutil.copy2(path, target)
        else:
            raise ValueError(f"Code root '{code_root}' contains a non-file entry: '{relative_path}'.")


def _stage_component_source(root: Path, destination: Path) -> None:
    if (root / _RUNNER_NAME).exists() or (root / _RUNNER_NAME).is_symlink():
        raise ValueError(f"Code root '{root}' contains the reserved runner name '{_RUNNER_NAME}'.")
    _copy_source_tree(root, destination, root, [])
    shutil.copyfile(Path(__file__).with_name("_component_runner.py"), destination / _RUNNER_NAME)
