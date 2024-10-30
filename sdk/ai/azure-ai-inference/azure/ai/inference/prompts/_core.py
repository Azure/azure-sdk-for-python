# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

import os
import re
import yaml
import json
import abc
from pathlib import Path
from .tracer import Tracer, trace, to_dict
from pydantic import BaseModel, Field, FilePath
from typing import AsyncIterator, Iterator, List, Literal, Dict, Callable, Set, TypeVar, Generic


T = TypeVar("T")


class SimpleModel(BaseModel, Generic[T]):
    """Simple model for a single item."""

    item: T


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class PropertySettings(BaseModel):
    """PropertySettings class to define the properties of the model

    Attributes
    ----------
    type : str
        The type of the property
    default : any
        The default value of the property
    description : str
        The description of the property
    """

    type: Literal["string", "number", "array", "object", "boolean"]
    default: str | int | float | List | dict | bool = Field(default=None)
    description: str = Field(default="")


class ModelSettings(BaseModel):
    """ModelSettings class to define the model of the prompty

    Attributes
    ----------
    api : str
        The api of the model
    configuration : dict
        The configuration of the model
    parameters : dict
        The parameters of the model
    response : dict
        The response of the model
    """

    api: str = Field(default="")
    configuration: dict = Field(default={})
    parameters: dict = Field(default={})
    response: dict = Field(default={})

    def model_dump(
        self,
        *,
        mode: str = "python",
        include: (
            Set[int] | Set[str] | Dict[int, os.Any] | Dict[str, os.Any] | None
        ) = None,
        exclude: (
            Set[int] | Set[str] | Dict[int, os.Any] | Dict[str, os.Any] | None
        ) = None,
        context: os.Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none"] | Literal["warn"] | Literal["error"] = True,
        serialize_as_any: bool = False,
    ) -> Dict[str, os.Any]:
        """Method to dump the model in a safe way"""
        d = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

        d["configuration"] = {
            k: "*" * len(v) if "key" in k.lower() or "secret" in k.lower() else v
            for k, v in d["configuration"].items()
        }
        return d


class TemplateSettings(BaseModel):
    """TemplateSettings class to define the template of the prompty

    Attributes
    ----------
    type : str
        The type of the template
    parser : str
        The parser of the template
    """

    type: str = Field(default="jinja2")
    parser: str = Field(default="")


class Prompty(BaseModel):
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
    sample : dict
        The sample of the prompty
    inputs : Dict[str, PropertySettings]
        The inputs of the prompty
    outputs : Dict[str, PropertySettings]
        The outputs of the prompty
    template : TemplateSettings
        The template of the prompty
    file : FilePath
        The file of the prompty
    content : str | List[str] | dict
        The content of the prompty
    """

    # metadata
    name: str = Field(default="")
    description: str = Field(default="")
    authors: List[str] = Field(default=[])
    tags: List[str] = Field(default=[])
    version: str = Field(default="")
    base: str = Field(default="")
    basePrompty: Prompty | None = Field(default=None)
    # model
    model: ModelSettings = Field(default_factory=ModelSettings)

    # sample
    sample: dict = Field(default={})

    # input / output
    inputs: Dict[str, PropertySettings] = Field(default={})
    outputs: Dict[str, PropertySettings] = Field(default={})

    # template
    template: TemplateSettings

    file: FilePath = Field(default="")
    content: str | List[str] | dict = Field(default="")

    def to_safe_dict(self) -> Dict[str, any]:
        d = {}
        for k, v in self:
            if v != "" and v != {} and v != [] and v != None:
                if k == "model":
                    d[k] = v.model_dump()
                elif k == "template":
                    d[k] = v.model_dump()
                elif k == "inputs" or k == "outputs":
                    d[k] = {k: v.model_dump() for k, v in v.items()}
                elif k == "file":
                    d[k] = (
                        str(self.file.as_posix())
                        if isinstance(self.file, Path)
                        else self.file
                    )
                elif k == "basePrompty":
                    # no need to serialize basePrompty
                    continue

                else:
                    d[k] = v
        return d

    @staticmethod
    def _process_file(file: str, parent: Path) -> any:
        file = Path(parent / Path(file)).resolve().absolute()
        if file.exists():
            with open(str(file), "r") as f:
                items = json.load(f)
                if isinstance(items, list):
                    return [Prompty.normalize(value, parent) for value in items]
                elif isinstance(items, dict):
                    return {
                        key: Prompty.normalize(value, parent)
                        for key, value in items.items()
                    }
                else:
                    return items
        else:
            raise FileNotFoundError(f"File {file} not found")

    @staticmethod
    def _process_env(variable: str, env_error=True, default: str = None) -> any:
        if variable in os.environ.keys():
            return os.environ[variable]
        else:
            if default:
                return default
            if env_error:
                raise ValueError(f"Variable {variable} not found in environment")

            return ""

    @staticmethod
    def normalize(attribute: any, parent: Path, env_error=True) -> any:
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
                    # old way of doing things for back compatibility
                    v = Prompty._process_env(variable[0], False)
                    if len(v) == 0:
                        if len(variable) > 1:
                            return variable[1]
                        else:
                            if env_error:
                                raise ValueError(
                                    f"Variable {variable[0]} not found in environment"
                                )
                            else:
                                return v
                    else:
                        return v
            elif (
                attribute.startswith("file:")
                and Path(parent / attribute.split(":")[1]).exists()
            ):
                # old way of doing things for back compatibility
                return Prompty._process_file(attribute.split(":")[1], parent)
            else:
                return attribute
        elif isinstance(attribute, list):
            return [Prompty.normalize(value, parent) for value in attribute]
        elif isinstance(attribute, dict):
            return {
                key: Prompty.normalize(value, parent)
                for key, value in attribute.items()
            }
        else:
            return attribute


def param_hoisting(
    top: Dict[str, any], bottom: Dict[str, any], top_key: str = None
) -> Dict[str, any]:
    if top_key:
        new_dict = {**top[top_key]} if top_key in top else {}
    else:
        new_dict = {**top}
    for key, value in bottom.items():
        if not key in new_dict:
            new_dict[key] = value
    return new_dict


class Invoker(abc.ABC):
    """Abstract class for Invoker

    Attributes
    ----------
    prompty : Prompty
        The prompty object
    name : str
        The name of the invoker

    """

    def __init__(self, prompty: Prompty) -> None:
        self.prompty = prompty
        self.name = self.__class__.__name__

    @abc.abstractmethod
    def invoke(self, data: any) -> any:
        """Abstract method to invoke the invoker

        Parameters
        ----------
        data : any
            The data to be invoked

        Returns
        -------
        any
            The invoked
        """
        pass

    @trace
    def __call__(self, data: any) -> any:
        """Method to call the invoker

        Parameters
        ----------
        data : any
            The data to be invoked

        Returns
        -------
        any
            The invoked
        """
        return self.invoke(data)


class InvokerFactory:
    """Factory class for Invoker"""

    _renderers: Dict[str, Invoker] = {}
    _parsers: Dict[str, Invoker] = {}
    _executors: Dict[str, Invoker] = {}
    _processors: Dict[str, Invoker] = {}

    @classmethod
    def has_invoker(
        cls, type: Literal["renderer", "parser", "executor", "processor"], name: str
    ) -> bool:
        if type == "renderer":
            return name in cls._renderers
        elif type == "parser":
            return name in cls._parsers
        elif type == "executor":
            return name in cls._executors
        elif type == "processor":
            return name in cls._processors
        else:
            raise ValueError(f"Type {type} not found")

    @classmethod
    def add_renderer(cls, name: str, invoker: Invoker) -> None:
        cls._renderers[name] = invoker

    @classmethod
    def add_parser(cls, name: str, invoker: Invoker) -> None:
        cls._parsers[name] = invoker

    @classmethod
    def add_executor(cls, name: str, invoker: Invoker) -> None:
        cls._executors[name] = invoker

    @classmethod
    def add_processor(cls, name: str, invoker: Invoker) -> None:
        cls._processors[name] = invoker

    @classmethod
    def register_renderer(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: Invoker) -> Callable:
            cls._renderers[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def register_parser(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: Invoker) -> Callable:
            cls._parsers[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def register_executor(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: Invoker) -> Callable:
            cls._executors[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def register_processor(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class: Invoker) -> Callable:
            cls._processors[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create_renderer(cls, name: str, prompty: Prompty) -> Invoker:
        if name not in cls._renderers:
            raise ValueError(f"Renderer {name} not found")
        return cls._renderers[name](prompty)

    @classmethod
    def create_parser(cls, name: str, prompty: Prompty) -> Invoker:
        if name not in cls._parsers:
            raise ValueError(f"Parser {name} not found")
        return cls._parsers[name](prompty)

    @classmethod
    def create_executor(cls, name: str, prompty: Prompty) -> Invoker:
        if name not in cls._executors:
            raise ValueError(f"Executor {name} not found")
        return cls._executors[name](prompty)

    @classmethod
    def create_processor(cls, name: str, prompty: Prompty) -> Invoker:
        if name not in cls._processors:
            raise ValueError(f"Processor {name} not found")
        return cls._processors[name](prompty)


class InvokerException(Exception):
    """Exception class for Invoker"""

    def __init__(self, message: str, type: str) -> None:
        super().__init__(message)
        self.type = type

    def __str__(self) -> str:
        return f"{super().__str__()}. Make sure to pip install any necessary package extras (i.e. could be something like `pip install prompty[{self.type}]`) for {self.type} as well as import the appropriate invokers (i.e. could be something like `import prompty.{self.type}`)."


@InvokerFactory.register_renderer("NOOP")
@InvokerFactory.register_parser("NOOP")
@InvokerFactory.register_executor("NOOP")
@InvokerFactory.register_processor("NOOP")
@InvokerFactory.register_parser("prompty.embedding")
@InvokerFactory.register_parser("prompty.image")
@InvokerFactory.register_parser("prompty.completion")
class NoOp(Invoker):
    def invoke(self, data: any) -> any:
        return data


class Frontmatter:
    """Frontmatter class to extract frontmatter from string."""

    _yaml_delim = r"(?:---|\+\+\+)"
    _yaml = r"(.*?)"
    _content = r"\s*(.+)$"
    _re_pattern = r"^\s*" + _yaml_delim + _yaml + _yaml_delim + _content
    _regex = re.compile(_re_pattern, re.S | re.M)

    @classmethod
    def read_file(cls, path):
        """Returns dict with separated frontmatter from file.

        Parameters
        ----------
        path : str
            The path to the file
        """
        with open(path, encoding="utf-8") as file:
            file_contents = file.read()
            return cls.read(file_contents)

    @classmethod
    def read(cls, string):
        """Returns dict with separated frontmatter from string.

        Parameters
        ----------
        string : str
            The string to extract frontmatter from


        Returns
        -------
        dict
            The separated frontmatter
        """
        fmatter = ""
        body = ""
        result = cls._regex.search(string)

        if result:
            fmatter = result.group(1)
            body = result.group(2)
        return {
            "attributes": yaml.safe_load(fmatter),
            "body": body,
            "frontmatter": fmatter,
        }


class PromptyStream(Iterator):
    """PromptyStream class to iterate over LLM stream.
    Necessary for Prompty to handle streaming data when tracing."""

    def __init__(self, name: str, iterator: Iterator):
        self.name = name
        self.iterator = iterator
        self.items: List[any] = []
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
        self.items: List[any] = []
        self.__name__ = "AsyncPromptyStream"

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            # enumerate but add to list
            o = await self.iterator.__anext__()
            self.items.append(o)
            return o

        except StopIteration:
            # StopIteration is raised
            # contents are exhausted
            if len(self.items) > 0:
                with Tracer.start("AsyncPromptyStream") as trace:
                    trace("signature", f"{self.name}.AsyncPromptyStream")
                    trace("inputs", "None")
                    trace("result", [to_dict(s) for s in self.items])

            raise StopIteration
