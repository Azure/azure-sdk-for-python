# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Convert an APIView ``api.md`` stub into a ``code_report.json`` style dict.

This lets the breaking-changes / changelog comparison logic run from the
``apistub`` generated ``api.md`` instead of importing the built package. The
output is functionally equivalent (not byte identical) to the report produced
by :mod:`detect_breaking_changes` ``build_library_report`` -- it carries the
public namespaces, classes, enums, methods/overloads, properties and module
level functions needed for diffing.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

_LOGGER = logging.getLogger(__name__)

_NAMESPACE_RE = re.compile(r"^namespace\s+(?P<name>[\w\.]+)\s*$")
_CLASS_RE = re.compile(r"^\s*class\s+(?P<fqn>[\w\.]+)\s*(?:\((?P<bases>.*)\))?\s*:")
_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(?P<name>[\w_]+)\s*\(")
_PROP_RE = re.compile(r"^\s*(?P<name>[A-Za-z_]\w*)\s*:\s*(?P<type>.+?)\s*$")
_ENUM_MEMBER_RE = re.compile(r"^\s*(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*(?P<value>.+?)\s*$")


def _is_enum(bases: Optional[str]) -> bool:
    return bool(bases) and "Enum" in bases


def _split_params(param_str: str) -> List[str]:
    """Split a parameter list on top level commas, ignoring brackets."""
    params, depth, current = [], 0, ""
    for char in param_str:
        if char in "[({":
            depth += 1
        elif char in "])}":
            depth -= 1
        if char == "," and depth == 0:
            params.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        params.append(current.strip())
    return params


def _parse_default(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    raw = raw.strip()
    if raw == "":
        return None
    # apistub renders hidden defaults as ``...``; treat it like a None default
    # so optional parameters match the import-based report.
    if raw in ("...", "None"):
        return "none"
    return raw.strip("\"'")


def _parse_parameters(param_str: str) -> Dict:
    parameters: Dict[str, Dict] = {}
    kind = "positional_or_keyword"
    for token in _split_params(param_str):
        if not token:
            continue
        if token == "*":
            kind = "keyword_only"
            continue
        if token == "/":
            continue
        if token.startswith("**"):
            name = token[2:].split(":")[0].strip()
            parameters[name] = {"type": None, "default": None, "param_type": "var_keyword"}
            continue
        if token.startswith("*"):
            name = token[1:].split(":")[0].strip()
            parameters[name] = {"type": None, "default": None, "param_type": "var_positional"}
            kind = "keyword_only"
            continue
        default = None
        if "=" in token:
            token, default = token.split("=", 1)
        annotation = None
        if ":" in token:
            name, annotation = token.split(":", 1)
            name = name.strip()
            annotation = annotation.strip() or None
            # Normalize ``Optional[X]`` to ``X`` so apistub-only optionality
            # does not produce spurious type-change entries. An optional param
            # with no explicit default is treated as defaulting to None.
            if annotation and annotation.startswith("Optional[") and annotation.endswith("]"):
                annotation = annotation[len("Optional[") : -1]
                if default is None:
                    default = "None"
        else:
            name = token.strip()
        if not name:
            continue
        if default is None and kind == "keyword_only":
            default = "None"
        parsed_default = _parse_default(default)
        if parsed_default not in (None, "none") and annotation and re.match(r"^Union\[str,\s*[^\]]+\]$", annotation):
            parsed_default = "str"
        parameters[name] = {"type": annotation, "default": parsed_default, "param_type": kind}

    def _sort_key(item: Tuple[str, Dict]) -> Tuple[int, str]:
        name, data = item
        if name == "self":
            return (0, "")
        if data["param_type"] == "var_positional":
            return (2, name)
        if data["param_type"] == "var_keyword":
            return (3, name)
        return (1, name)

    return dict(sorted(parameters.items(), key=_sort_key))


def _parse_signature(block: str) -> Tuple[str, Dict]:
    """Parse a ``def`` block, returning the method name and a function report."""
    match = _DEF_RE.match(block)
    name = match.group("name") if match else ""
    is_async = bool(re.match(r"^\s*async\s+def", block))
    open_paren = block.index("(")
    depth, end = 0, len(block)
    for i in range(open_paren, len(block)):
        if block[i] == "(":
            depth += 1
        elif block[i] == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    param_str = block[open_paren + 1 : end]
    return_type = None
    arrow = block.find("->", end)
    if arrow != -1:
        return_type = block[arrow + 2 :].split(":")[0].strip() or None
    return name, {
        "parameters": _parse_parameters(param_str),
        "is_async": is_async,
        "return_type": return_type,
        "overloads": [],
    }


def parse_api_md(content: str) -> Dict:
    """Parse the contents of an ``api.md`` file into a code report dict."""
    report: Dict[str, Dict] = {}
    module: Optional[str] = None
    cls: Optional[str] = None
    cls_is_enum = False
    pending_overload = False
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        ns = _NAMESPACE_RE.match(line)
        if ns:
            module = ns.group("name") or ""
            report.setdefault(module, {"class_nodes": {}, "function_nodes": {}})
            cls = None
            i += 1
            continue

        if module is None:
            i += 1
            continue

        cls_match = _CLASS_RE.match(line)
        if cls_match:
            fqn = cls_match.group("fqn")
            cls = fqn.split(".")[-1]
            cls_is_enum = _is_enum(cls_match.group("bases"))
            report[module]["class_nodes"][cls] = {
                "type": "Enum" if cls_is_enum else None,
                "methods": {},
                "properties": {},
            }
            i += 1
            continue

        if stripped == "@overload":
            pending_overload = True
            i += 1
            continue
        if stripped.startswith("@"):
            i += 1
            continue

        if _DEF_RE.match(line):
            block, i = _collect_block(lines, i)
            name, func = _parse_signature(block)
            indent = len(line) - len(line.lstrip())
            if cls and indent > 0:
                methods = report[module]["class_nodes"][cls]["methods"]
                # Match the import-based report which only keeps public methods
                # plus ``__init__``. Synthesized model ``__init__`` exists for
                # every model in the import-based report on both sides, so only
                # keep ``__init__`` for clients/operations to avoid churn.
                if name == "__init__" and not (cls.endswith("Client") or cls.endswith("Operations")):
                    pending_overload = False
                    continue
                if name.startswith("_") and not name.startswith("__init__"):
                    pending_overload = False
                    continue
                if pending_overload:
                    methods.setdefault(
                        name, {"parameters": {}, "is_async": func["is_async"], "return_type": None, "overloads": []}
                    )
                    if not methods[name]["parameters"]:
                        methods[name].update({k: func[k] for k in ("parameters", "is_async", "return_type")})
                    methods[name]["overloads"].append({k: func[k] for k in ("parameters", "is_async", "return_type")})
                else:
                    func.setdefault("overloads", [])
                    existing = methods.get(name)
                    if existing and existing.get("overloads") and set(func["parameters"]) <= {"self", "args", "kwargs"}:
                        pending_overload = False
                        continue
                    methods[name] = func
            else:
                if name.startswith("_") and not name.startswith("__init__"):
                    pending_overload = False
                    continue
                report[module]["function_nodes"][name] = func
            pending_overload = False
            continue

        if cls and cls_is_enum:
            member = _ENUM_MEMBER_RE.match(line)
            if member:
                report[module]["class_nodes"][cls]["properties"][member.group("name")] = member.group("name")
        elif cls:
            prop = _PROP_RE.match(line)
            if prop and len(line) - len(line.lstrip()) >= 8:
                report[module]["class_nodes"][cls]["properties"][prop.group("name")] = {"attr_type": prop.group("type")}
        i += 1
    return report


def _collect_block(lines: List[str], start: int) -> Tuple[str, int]:
    """Join a (possibly multi-line) def block until it ends with ``: ...``."""
    block = lines[start]
    i = start
    while ": ..." not in block and not block.rstrip().endswith(":"):
        i += 1
        if i >= len(lines):
            break
        block += " " + lines[i].strip()
    return block, i + 1


def convert_api_md_to_report(api_md_path: str) -> Dict:
    with open(api_md_path, "r", encoding="utf-8") as fd:
        content = fd.read()
    return parse_api_md(content)
