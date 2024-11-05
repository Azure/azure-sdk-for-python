# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="assignment,attr-defined,index,arg-type"
# pylint: disable=line-too-long,R,consider-iterating-dictionary,raise-missing-from,dangerous-default-value
from __future__ import annotations
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Union
from ._tracer import Tracer, to_dict
from ._utils import load_json


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass
class PropertySettings:
    """PropertySettings class to define the properties of the model

    Attributes
    ----------
    type : str
        The type of the property
    default : Any
        The default value of the property
    description : str
        The description of the property
    """

    type: Literal["string", "number", "array", "object", "boolean"]
    default: Union[str, int, float, List, Dict, bool, None] = field(default=None)
    description: str = field(default="")


@dataclass
class ModelSettings:
    """ModelSettings class to define the model of the prompty

    Attributes
    ----------
    api : str
        The api of the model
    configuration : Dict
        The configuration of the model
    parameters : Dict
        The parameters of the model
    response : Dict
        The response of the model
    """

    api: str = field(default="")
    configuration: Dict = field(default_factory=dict)
    parameters: Dict = field(default_factory=dict)
    response: Dict = field(default_factory=dict)


@dataclass
class TemplateSettings:
    """TemplateSettings class to define the template of the prompty

    Attributes
    ----------
    type : str
        The type of the template
    parser : str
        The parser of the template
    """

    type: str = field(default="mustache")
    parser: str = field(default="")


@dataclass
class Prompty:
    """Prompty class to define the prompty

    Attributes
    ----------
    name : str
        The name of the prompty
    description : str
        The description of the prompty
    authors : List[str]
        The authors of the prompty
    tags : List[str]
        The tags of the prompty
    version : str
        The version of the prompty
    base : str
        The base of the prompty
    basePrompty : Prompty
        The base prompty
    model : ModelSettings
        The model of the prompty
    sample : Dict
        The sample of the prompty
    inputs : Dict[str, PropertySettings]
        The inputs of the prompty
    outputs : Dict[str, PropertySettings]
        The outputs of the prompty
    template : TemplateSettings
        The template of the prompty
    file : FilePath
        The file of the prompty
    content : Union[str, List[str], Dict]
        The content of the prompty
    """

    # metadata
    name: str = field(default="")
    description: str = field(default="")
    authors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = field(default="")
    base: str = field(default="")
    basePrompty: Union[Prompty, None] = field(default=None)
    # model
    model: ModelSettings = field(default_factory=ModelSettings)

    # sample
    sample: Dict = field(default_factory=dict)

    # input / output
    inputs: Dict[str, PropertySettings] = field(default_factory=dict)
    outputs: Dict[str, PropertySettings] = field(default_factory=dict)

    # template
    template: TemplateSettings = field(default_factory=TemplateSettings)

    file: Union[Path, str] = field(default="")
    content: Union[str, List[str], Dict] = field(default="")

    def to_safe_dict(self) -> Dict[str, Any]:
        d = {}
        if self.model:
            d["model"] = asdict(self.model)
            _mask_secrets(d, ["model", "configuration"])
        if self.template:
            d["template"] = asdict(self.template)
        if self.inputs:
            d["inputs"] = {k: asdict(v) for k, v in self.inputs.items()}
        if self.outputs:
            d["outputs"] = {k: asdict(v) for k, v in self.outputs.items()}
        if self.file:
            d["file"] = str(self.file.as_posix()) if isinstance(self.file, Path) else self.file
        return d

    @staticmethod
    def hoist_base_prompty(top: Prompty, base: Prompty) -> Prompty:
        top.name = base.name if top.name == "" else top.name
        top.description = base.description if top.description == "" else top.description
        top.authors = list(set(base.authors + top.authors))
        top.tags = list(set(base.tags + top.tags))
        top.version = base.version if top.version == "" else top.version

        top.model.api = base.model.api if top.model.api == "" else top.model.api
        top.model.configuration = param_hoisting(top.model.configuration, base.model.configuration)
        top.model.parameters = param_hoisting(top.model.parameters, base.model.parameters)
        top.model.response = param_hoisting(top.model.response, base.model.response)

        top.sample = param_hoisting(top.sample, base.sample)

        top.basePrompty = base

        return top

    @staticmethod
    def _process_file(file: str, parent: Path) -> Any:
        file_path = Path(parent / Path(file)).resolve().absolute()
        if file_path.exists():
            items = load_json(file_path)
            if isinstance(items, list):
                return [Prompty.normalize(value, parent) for value in items]
            elif isinstance(items, Dict):
                return {key: Prompty.normalize(value, parent) for key, value in items.items()}
            else:
                return items
        else:
            raise FileNotFoundError(f"File {file} not found")

    @staticmethod
    def _process_env(variable: str, env_error=True, default: Union[str, None] = None) -> Any:
        if variable in os.environ.keys():
            return os.environ[variable]
        else:
            if default:
                return default
            if env_error:
                raise ValueError(f"Variable {variable} not found in environment")

            return ""

    @staticmethod
    def normalize(attribute: Any, parent: Path, env_error=True) -> Any:
        if isinstance(attribute, str):
            attribute = attribute.strip()
            if attribute.startswith("${") and attribute.endswith("}"):
                # check if env or file
                variable = attribute[2:-1].split(":")
                if variable[0] == "env" and len(variable) > 1:
                    return Prompty._process_env(
                        variable[1],
                        env_error,
                        variable[2] if len(variable) > 2 else None,
                    )
                elif variable[0] == "file" and len(variable) > 1:
                    return Prompty._process_file(variable[1], parent)
                else:
                    raise ValueError(f"Invalid attribute format ({attribute})")
            else:
                return attribute
        elif isinstance(attribute, list):
            return [Prompty.normalize(value, parent) for value in attribute]
        elif isinstance(attribute, Dict):
            return {key: Prompty.normalize(value, parent) for key, value in attribute.items()}
        else:
            return attribute


def param_hoisting(top: Dict[str, Any], bottom: Dict[str, Any], top_key: Union[str, None] = None) -> Dict[str, Any]:
    if top_key:
        new_dict = {**top[top_key]} if top_key in top else {}
    else:
        new_dict = {**top}
    for key, value in bottom.items():
        if not key in new_dict:
            new_dict[key] = value
    return new_dict


class PromptyStream(Iterator):
    """PromptyStream class to iterate over LLM stream.
    Necessary for Prompty to handle streaming data when tracing."""

    def __init__(self, name: str, iterator: Iterator):
        self.name = name
        self.iterator = iterator
        self.items: List[Any] = []
        self.__name__ = "PromptyStream"

    def __iter__(self):
        return self

    def __next__(self):
        try:
            # enumerate but add to list
            o = self.iterator.__next__()
            self.items.append(o)
            return o

        except StopIteration:
            # StopIteration is raised
            # contents are exhausted
            if len(self.items) > 0:
                with Tracer.start("PromptyStream") as trace:
                    trace("signature", f"{self.name}.PromptyStream")
                    trace("inputs", "None")
                    trace("result", [to_dict(s) for s in self.items])

            raise StopIteration


class AsyncPromptyStream(AsyncIterator):
    """AsyncPromptyStream class to iterate over LLM stream.
    Necessary for Prompty to handle streaming data when tracing."""

    def __init__(self, name: str, iterator: AsyncIterator):
        self.name = name
        self.iterator = iterator
        self.items: List[Any] = []
        self.__name__ = "AsyncPromptyStream"

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            # enumerate but add to list
            o = await self.iterator.__anext__()
            self.items.append(o)
            return o

        except StopAsyncIteration:
            # StopIteration is raised
            # contents are exhausted
            if len(self.items) > 0:
                with Tracer.start("AsyncPromptyStream") as trace:
                    trace("signature", f"{self.name}.AsyncPromptyStream")
                    trace("inputs", "None")
                    trace("result", [to_dict(s) for s in self.items])

            raise StopAsyncIteration


def _mask_secrets(d: Dict[str, Any], path: list[str], patterns: list[str] = ["key", "secret"]) -> bool:
    sub_d = d
    for key in path:
        if key not in sub_d:
            return False
        sub_d = sub_d[key]

    for k, v in sub_d.items():
        if any([pattern in k.lower() for pattern in patterns]):
            sub_d[k] = "*" * len(v)
    return True
