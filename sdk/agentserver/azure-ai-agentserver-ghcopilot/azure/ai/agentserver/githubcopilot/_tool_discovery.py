# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Auto-discover tools from ``.github/tools/`` directories.

Each tool is a directory containing:

* ``TOOL.md`` -- YAML frontmatter with *name*, *description*, *parameters*
* ``tool.py`` -- Python module exporting an async ``handler(invocation)``

Discovery mirrors the skills pattern: scan ``tools/*/TOOL.md``, parse the
YAML frontmatter for the schema, and dynamically import ``tool.py`` for the
handler.
"""

import importlib.util
import logging
import pathlib
import sys
from typing import Any, List, Tuple

import yaml

from copilot.tools import Tool

logger = logging.getLogger(__name__)


def _parse_frontmatter(path: pathlib.Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


def _load_handler(tool_dir: pathlib.Path) -> Any:
    """Dynamically import ``tool.py`` and return the module."""
    tool_py = tool_dir / "tool.py"
    if not tool_py.exists():
        raise FileNotFoundError(f"No tool.py in {tool_dir}")

    module_name = f"_tool_{tool_dir.name}"
    spec = importlib.util.spec_from_file_location(module_name, str(tool_py))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    if not hasattr(module, "handler"):
        raise AttributeError(f"tool.py in {tool_dir} must define an async 'handler' function")

    return module


def discover_tools(project_root: pathlib.Path) -> Tuple[List[Tool], List[Any]]:
    """Scan ``.github/tools/`` for tool directories and return SDK Tool objects.

    :param project_root: Root directory of the agent project.
    :return: ``(tools, modules)`` -- list of :class:`copilot.Tool` objects and
        their loaded Python modules.
    """
    tools_dir = project_root / ".github" / "tools"
    if not tools_dir.exists():
        return [], []

    tools: List[Tool] = []
    modules: List[Any] = []

    for tool_dir in sorted(tools_dir.iterdir()):
        tool_md = tool_dir / "TOOL.md"
        if not tool_dir.is_dir() or not tool_md.exists():
            continue

        try:
            meta = _parse_frontmatter(tool_md)
            name = meta.get("name", tool_dir.name)
            description = meta.get("description", "")
            parameters = meta.get("parameters", {})

            module = _load_handler(tool_dir)

            tool = Tool(
                name=name,
                description=description,
                parameters=parameters,
                handler=module.handler,
            )
            tools.append(tool)
            modules.append(module)
            logger.info("Discovered tool: %s (%s)", name, tool_dir)

        except Exception:
            logger.warning("Failed to load tool from %s", tool_dir, exc_info=True)

    return tools, modules
