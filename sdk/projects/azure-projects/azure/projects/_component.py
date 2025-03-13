# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from concurrent.futures import ThreadPoolExecutor
import asyncio
import sys
import threading
import keyword
import types
from typing import (
    Coroutine,
    Generic,
    Mapping,
    MutableMapping,
    Protocol,
    Any,
    Tuple,
    Union,
    Literal,
    Optional,
    List,
    Type,
    overload,
)
from typing_extensions import Self, TypeVar, dataclass_transform

from ._bicep.expressions import Parameter, MISSING, Default
from ._resource import Resource, _load_dev_environment, SyncClient, AsyncClient
from .resources import RESOURCE_FROM_CLIENT_ANNOTATION
from .resources.resourcegroup import ResourceGroup
from .resources.managedidentity import UserAssignedIdentity
from .resources.appconfig import ConfigStore


# Raised when an attempt is made to modify a frozen class.
class FrozenInstanceError(AttributeError):
    pass


def get_annotations(cls: Type) -> Mapping[str, Any]:
    # This is needed for Python <3.10
    try:
        from inspect import get_annotations as _get_annotations  # type: ignore[attr-defined]

        return _get_annotations(cls)
    except ImportError:
        pass
    try:
        return cls.__annotations__
    except AttributeError:
        pass
    return {}


def get_mro_annotations(cls: Type, base_cls: Type) -> Mapping[str, Tuple[Any, Any]]:
    mro = cls.mro()
    return {
        attr: (ann, t.__dict__.get(attr))
        for t in reversed(mro[: mro.index(base_cls) + 1])
        for attr, ann in get_annotations(t).items()
    }


class DefaultFactory(Protocol):
    __name__: str

    def __call__(self, **kwargs) -> Any: ...


class AsyncDefaultFactory(Protocol):
    __name__: str

    async def __call__(self, **kwargs) -> Any: ...


class ComponentField(Parameter):
    def __init__(
        self,
        *,
        default: Any,
        factory: Union[Literal[Default.MISSING], DefaultFactory, AsyncDefaultFactory],
        repr: bool,
        init: bool,
        alias: Optional[str],
        **kwargs,
    ):
        # TODO: make Parameter name optional?
        super().__init__("", default=default)
        self._factory = factory
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None
        self._name: Optional[str] = None
        self.kwargs = kwargs
        self.repr = repr
        self.init = init
        self.alias = alias

    @property
    def name(self) -> str:
        if not self._owner or not self._name:
            raise ValueError("ComponentField not used in component class.")
        return f"{self._owner.__name__}.{self._name}"

    @property
    def value(self) -> str:
        return ""

    def __repr__(self) -> str:
        if self.default is not MISSING:
            return f"Field(default={repr(self.default)})"
        if self._factory is not MISSING:
            return f"Field(default={getattr(self._factory, '__name__', 'factory')}(**kwargs))"
        return "Field()"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name
        self._attrname = "_field__" + name

    async def _run_factory(self):
        factory = self._factory(**self.kwargs)
        try:
            await factory
        except TypeError:
            return factory

    def __get__(
        self,
        obj,
        _,
    ):
        if obj is None:
            if self.default is not MISSING:
                return self.default
            if self._factory is not MISSING:
                return run_coroutine_sync(self._run_factory())
            raise AttributeError(f"No default value provided for '{self._owner.__name__}.{self._name}'.")
        return getattr(obj, self._attrname)

    def __set__(self, obj, value):
        object.__setattr__(obj, self._attrname, value)

    def get(self, obj: Optional["AzureInfrastructure"] = None, /) -> Any:
        return self.__get__(obj, obj.__class__)


def field(
    *,
    default=MISSING,
    factory=MISSING,
    repr=True,
    init=True,
    alias=None,
    **kwargs,
):
    if default is not MISSING and factory is not MISSING:
        raise ValueError("Cannot specify both 'default' and 'factory'.")
    if alias and not init:
        raise ValueError("Alias is only supported if init=True.")
    return ComponentField(default=default, factory=factory, repr=repr, init=init, alias=alias, **kwargs)


@dataclass_transform(
    field_specifiers=(field,), eq_default=False, order_default=False, kw_only_default=True, frozen_default=True
)
class AzureInfraComponent(type):
    # TODO: The typing of the __call__ function is breaking
    # typing when kwargs are passed into the constructor.
    # Need to figure that out.....
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        child_infra_components = []
        repr_objects = []
        for attr, (_, attr_field) in get_mro_annotations(  # pylint: disable=too-many-nested-blocks
            cls, AzureInfrastructure
        ).items():
            include_in_repr = True
            try:
                if isinstance(attr_field, ComponentField):
                    # This attribute has used the `field()` specifier to define the default behaviour.
                    if not attr_field.repr:
                        include_in_repr = False
                    if not attr_field.init:
                        # This field should not be passed into the init - we don't pop from kwargs. If it was
                        # passed in, it will be flagged as an unexpected keyword. If there's no default, this
                        # will raise an AttributeError
                        value = getattr(cls, attr)
                    else:
                        try:
                            # First we attempt to use a keyword-arg passed into the constructor,
                            # either by name or by alias.
                            if attr_field.alias:
                                value = kwargs.pop(attr_field.alias)
                            else:
                                value = kwargs.pop(attr)
                        except KeyError:
                            # If no kwarg was passed in, attempt to use a default. If there's no default, this will
                            # raise an AttributeError, handled below.
                            value = getattr(cls, attr)
                else:
                    # This attribute either uses a naked default or no default.
                    try:
                        # First we attempt to use a keyword-arg passed into the constructor.
                        value = kwargs.pop(attr)
                    except KeyError:
                        # If no kwarg was passed in, attempt to use a default. If there's no default, this will
                        # raise an AttributeError, handled below.
                        value = getattr(cls, attr)
            except AttributeError:
                missing_kwargs.append(attr)
            else:
                if include_in_repr:
                    repr_objects.append(f"{attr}={repr(value)}")
                if isinstance(value, AzureInfrastructure):
                    child_infra_components.append(value)
                instance_kwargs[attr] = value
                if attr in missing_kwargs:
                    missing_kwargs.pop(missing_kwargs.index(attr))

        if kwargs:
            # Any kwargs that haven't been popped yet are unexpected - raise a TypeError
            argument = "argument" if len(kwargs) == 1 else "arguments"
            args = ", ".join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            # Any annotations not specified and without a default are required - raise a TypeError
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ", ".join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")

        instance_kwargs["_repr_str"] = ", ".join(repr_objects)
        instance = super().__call__(**instance_kwargs)
        # This is used for internal linking of infra components. It should only matter if infra components
        # are instantiated in a field default, as it's only used to resolve ComponentField references.
        for infra_instance in child_infra_components:
            if infra_instance._parent:
                raise ValueError(f"AzureInfrastructure instance {value} already referenced by another object.")
            object.__setattr__(infra_instance, "_parent", instance)
        return instance


class AzureInfrastructure(metaclass=AzureInfraComponent):
    _parent: Optional["AzureInfrastructure"] = field(default=None, init=False, repr=False)
    _repr_str: str = field(default="", init=False, repr=False)
    resource_group: ResourceGroup = field(default=ResourceGroup(), repr=False)
    identity: Optional[UserAssignedIdentity] = field(default=UserAssignedIdentity(), repr=False)
    config_store: Optional[ConfigStore] = field(default=None, repr=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._repr_str})"

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, ComponentField):
            if self._parent:
                return attr.get(self._parent)
            # TODO: Ideally we should raise here, but doing so prevents
            # getattr calls within the class definition (i.e. before the object has
            # been instantiated).
            # raise AttributeError(f"Referenced attribute {repr(attr)} cannot be resolved.")
        return attr

    def __setattr__(self, name, value):
        raise FrozenInstanceError(f"Cannot assign to field {name!r}")

    def __delattr__(self, name):
        raise FrozenInstanceError(f"Cannot delete field {name!r}")

    def down(self, *, purge: bool = False) -> None:
        from ._provision import deprovision

        deprovision(self, purge=purge)


def make_infra(cls_name, fields, *, bases=(), namespace=None, module=None) -> Type[AzureInfrastructure]:
    # pylint: disable=protected-access
    # This code is taken from stdlib dataclasses.make_dataclass.
    if namespace is None:
        namespace = {}
    # TODO: Are the bases ordered backwards?
    bases = (AzureInfrastructure, *bases)
    # While we're looking through the field names, validate that they
    # are identifiers, are not keywords, and not duplicates.
    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = "typing.Any"
        elif len(item) == 2:
            (
                name,
                tp,
            ) = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f"Invalid field: {item!r}")

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f"Field names must be valid identifiers: {name!r}")
        if keyword.iskeyword(name):
            raise TypeError(f"Field names must not be keywords: {name!r}")
        if name in seen:
            raise TypeError(f"Field name duplicated: {name!r}")

        seen.add(name)
        annotations[name] = tp

    # Update 'ns' with the user-supplied namespace plus our calculated values.
    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns["__annotations__"] = annotations

    # We use `types.new_class()` instead of simply `type()` to allow dynamic creation
    # of generic dataclasses.
    cls = types.new_class(cls_name, bases, {}, exec_body_callback)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the dataclass is created.
    if module is None:
        try:
            module = sys._getframemodulename(1) or "__main__"  # type: ignore[attr-defined]
        except AttributeError:
            try:
                module = sys._getframe(1).f_globals.get("__name__", "__main__")
            except (AttributeError, ValueError):
                pass
    if module is not None:
        cls.__module__ = module
    return cls


@dataclass_transform(
    field_specifiers=(field,), eq_default=False, order_default=False, kw_only_default=True, frozen_default=True
)
class AzureAppComponent(type):
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        repr_objects = []
        for attr, (annotation, attr_field) in get_mro_annotations(  # pylint: disable=too-many-nested-blocks
            cls, AzureApp
        ).items():
            try:
                include_in_repr = True
                client_kwargs = {}
                if isinstance(attr_field, ComponentField):
                    # This attribute has used the `field()` specifier to define the default behaviour.
                    if not attr_field.repr:
                        include_in_repr = False
                    if not attr_field.init:
                        # This field should not be passed into the init - we don't pop from kwargs. If it was
                        # passed in, it will be flagged as an unexpected keyword. If there's no default, this will
                        # raise an AttributeError
                        value = getattr(cls, attr)
                    else:
                        try:
                            # First we attempt to use a keyword-arg passed into the constructor,
                            # either by name or by alias.
                            if attr_field.alias:
                                value = kwargs.pop(attr_field.alias)
                            else:
                                value = kwargs.pop(attr)
                        except KeyError:
                            # If no kwarg was passed in, attempt to use a default. If there's no default, this will
                            # raise an AttributeError, handled below.
                            value = getattr(cls, attr)
                    # We'll store these now in case we need them for a get_client call.
                    client_kwargs = attr_field.kwargs
                else:
                    # This attribute either uses a naked default or no default.
                    try:
                        # First we attempt to use a keyword-arg passed into the constructor.
                        value = kwargs.pop(attr)
                    except KeyError:
                        # If no kwarg was passed in, attempt to use a default. If there's no default, this will
                        # raise an AttributeError, handled below.
                        value = getattr(cls, attr)
            except AttributeError:
                missing_kwargs.append(attr)
            else:
                if isinstance(value, Resource) and annotation != value.__class__:
                    # This should filter out any cases of a type annotation for the resource itself, in
                    # which case we don't want to try and extract a client.
                    # TODO: This wont work for string annotations or Optional/Union.
                    # Because of how we merge annotations in get_mro_annotations, config_store and closeables should
                    # already be processed by the time we get to any resources defined the app.
                    client, credential = value.get_client(
                        annotation,
                        config_store=instance_kwargs.get("config_store"),
                        return_credential=True,
                        **client_kwargs,
                    )
                    instance_kwargs["_closeables"].extend([client, credential])
                    instance_kwargs[attr] = client
                    if include_in_repr:
                        repr_objects.append(f"{attr}={client.__class__.__name__}(...)")
                else:
                    instance_kwargs[attr] = value
                    if include_in_repr:
                        repr_objects.append(f"{attr}={repr(value)}")
                if attr in missing_kwargs:
                    missing_kwargs.pop(missing_kwargs.index(attr))
        if kwargs:
            argument = "argument" if len(kwargs) == 1 else "arguments"
            args = ", ".join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ", ".join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")
        return super().__call__(**instance_kwargs)


T = TypeVar("T")


def run_coroutine_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    # TODO: Found this on StackOverflow - needs further inspection
    # https://stackoverflow.com/questions/55647753/call-async-function-from-sync-function-while-the-synchronous-function-continues

    def run_in_new_loop():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        with ThreadPoolExecutor() as pool:
            future = pool.submit(run_in_new_loop)
            return future.result(timeout=timeout)
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()


InfrastructureType = TypeVar("InfrastructureType", bound=AzureInfrastructure, default=AzureInfrastructure)


class AzureApp(Generic[InfrastructureType], metaclass=AzureAppComponent):
    # TODO: As these will have classattribute defaults, need to test behaviour
    # Might need to build a specifier object or use field
    _infra: Optional[InfrastructureType] = field(alias="infra", default=None, repr=False)
    _closeables: List[Union[SyncClient, AsyncClient]] = field(factory=list, init=False, repr=False)
    _repr_str: str = field(default="", init=False, repr=False)
    config_store: Mapping[str, Any] = field(factory=dict, repr=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @property
    def infra(self) -> InfrastructureType:
        if self._infra is None:
            raise ValueError("AzureApp has no associated Infrastructure object.")
        return self._infra

    @overload
    @classmethod
    def load(
        cls,
        *,
        config_store: Optional[MutableMapping[str, Any]] = None,
        env_name: Optional[str] = None,
    ) -> Self: ...
    @overload
    @classmethod
    def load(
        cls,
        infra: InfrastructureType,
        attr_map: Optional[Mapping[str, str]] = None,
        *,
        config_store: Optional[MutableMapping[str, Any]] = None,
        env_name: Optional[str] = None,
    ) -> Self: ...
    @classmethod
    def load(
        cls,
        infra=None,
        attr_map=None,
        *,
        config_store=None,
        env_name=None,
    ):
        if attr_map and not infra:
            raise ValueError("Cannot specify attr_map without providing infrastructure object.")
        attr_map = attr_map or {}
        config_store = config_store or {}
        if not infra:
            env_name = env_name or cls.__name__
            fields = []
            for attr, annotation in get_annotations(cls).items():
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
                    resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                    attr_map[attr] = attr
                    fields.append((attr, resource_cls, field(default=resource_cls())))
            infra = make_infra(f"AutoInfra{cls.__name__}", fields)()
        if attr_map:
            kwargs = {c_attr: getattr(infra, i_attr) for c_attr, i_attr in attr_map.items()}
        else:
            infra_resources = {r.identifier: r for r in infra.__dict__.values() if isinstance(r, Resource)}
            kwargs = {}
            for attr, annotation in get_annotations(cls).items():
                # TODO: Duplicate annotation traversal - needs revising
                # TODO: Currently this doesn't support other type hints like Union/Optional
                # TODO: This doesn't support alias
                if (
                    annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION
                    and RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__] in infra_resources
                ):
                    kwargs[attr] = infra_resources[RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__]]

        # TODO: duplicate config loading
        config_store.update(_load_dev_environment(infra.__class__.__name__))
        return cls(config_store=config_store, infra=infra, **kwargs)

    @overload
    @classmethod
    def provision(
        cls,
        *,
        config_store: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Self: ...
    @overload
    @classmethod
    def provision(
        cls,
        infra: InfrastructureType,
        *,
        attr_map: Optional[Mapping[str, str]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Self: ...
    @classmethod
    def provision(
        cls,
        infra=None,
        *,
        attr_map=None,
        config_store=None,
        **kwargs,
    ):
        if attr_map and not infra:
            raise ValueError("Cannot specify attr_map without providing infrastructure object.")
        from ._provision import provision

        if not infra:
            attr_map = {}
            fields = []
            for attr, annotation in get_annotations(cls).items():
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
                    resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                    attr_map[attr] = attr
                    fields.append((attr, resource_cls, field(default=resource_cls())))
            infra = make_infra(f"_{cls.__name__}Infra", fields)()
        provision(infra, config_store=config_store, **kwargs)
        return cls.load(infra, attr_map=attr_map, config_store=config_store)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._repr_str})"

    def __setattr__(self, name, _):
        raise FrozenInstanceError(f"Cannot assign to field {name!r}")

    def __delattr__(self, name):
        raise FrozenInstanceError(f"Cannot delete field {name!r}")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.aclose()

    async def _close_client(self, client):
        closer = client.close()
        try:
            await closer
        except TypeError:
            pass

    def close(self) -> None:
        # We only close clients we instantiated via Resource.get_client()
        # If a client was either passed directly to the constructor, or returned
        # from a field default or factory, it is assumed that we don't own it.
        run_coroutine_sync(self.aclose())

    async def aclose(self) -> None:
        await asyncio.gather(*[self._close_client(c) for c in self._closeables])
