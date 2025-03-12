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
        self._kwargs = kwargs
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None
        self._name: Optional[str] = None
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
            return f"Field(default={getattr(self._factory.__name__, 'factory')}(**kwargs))"
        return "Field()"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name
        self._attrname = "_field__" + name
        # TODO: Don't think we need this.
        # try:
        #     self._type = get_annotations(owner)[name]
        # except KeyError:
        #     raise RuntimeError(f"'{owner.__name__}.{name}' is missing type hint.") from None

    async def _run_factory(self):
        factory = self._factory(**self._kwargs)
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
        setattr(obj, self._attrname, value)

    def get(self, obj: Optional["AzureInfrastructure"] = None, /) -> Any:
        return self.__get__(obj, obj.__class__)


def field(
    *,
    default=MISSING,
    factory=MISSING,
    repr=True,
    init=True,  # TODO: Support init
    alias=None,
    **kwargs,
):
    if default is not MISSING and factory is not MISSING:
        raise ValueError("Cannot specify both 'default' and 'factory'.")
    return ComponentField(default=default, factory=factory, repr=repr, init=init, alias=alias, **kwargs)


@dataclass_transform(field_specifiers=(field,), kw_only_default=True)
class AzureInfraComponent(type):
    # TODO: The typing of the __call__ function is breaking
    # typing when kwargs are passed into the constructor.
    # Need to figure that out.....
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        child_infra_components = []
        mro = cls.mro()
        # We want to skip objects in the heirachy above AzureInfrastructure, which should
        # only be 'object', but just in case that changes, we'll strip everything.
        for cls_type in mro[: mro.index(AzureInfrastructure) + 1]:
            for attr in get_annotations(cls_type):
                if attr in instance_kwargs:
                    continue
                try:
                    try:
                        instance_kwargs[attr] = kwargs.pop(attr)
                    except KeyError:
                        if (
                            attr in cls.__dict__
                            and isinstance(cls.__dict__[attr], ComponentField)
                            and cls.__dict__[attr].alias in kwargs
                        ):
                            # TODO: Should we be resolving the alias here, or in the init?
                            instance_kwargs[attr] = kwargs.pop(cls.__dict__[attr].alias)
                        else:
                            default_attr = getattr(cls, attr)
                            if isinstance(default_attr, AzureInfrastructure):
                                child_infra_components.append(default_attr)
                            instance_kwargs[attr] = default_attr
                    if attr in missing_kwargs:
                        missing_kwargs.pop(missing_kwargs.index(attr))
                except AttributeError:
                    missing_kwargs.append(attr)
        if kwargs:
            argument = "argument" if len(missing_kwargs) == 1 else "arguments"
            args = ", ".join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ", ".join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")
        kwargs.update(instance_kwargs)
        # Because the order of resources is important, we always want to make
        # 'resource_group' and 'identity' first.
        resource_group = kwargs.pop("resource_group")
        identity = kwargs.pop("identity")
        value = super().__call__(resource_group=resource_group, identity=identity, **kwargs)
        # This is used for internal linking of infra components, it should only matter if infra components
        # are instantiated in a field default.
        for infra_instance in child_infra_components:
            infra_instance._parent = value
        return value


class AzureInfrastructure(metaclass=AzureInfraComponent):
    _parent: Optional["AzureInfrastructure"] = field(default=None, init=False, repr=False)
    resource_group: ResourceGroup = field(default=ResourceGroup(), repr=False)
    identity: Optional[UserAssignedIdentity] = field(default=UserAssignedIdentity(), repr=False)
    config_store: Optional[ConfigStore] = field(default=None)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        attrs = []
        for attr in get_annotations(self.__class__):
            try:
                in_repr = self.__class__.__dict__[attr].repr
                if in_repr:
                    attrs.append(f"{attr}={repr(getattr(self, attr))}")
            except (KeyError, AttributeError):
                attrs.append(f"{attr}={repr(getattr(self, attr))}")
        repr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}({repr_str})"

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


@dataclass_transform(field_specifiers=(field,), kw_only_default=True)
class AzureAppComponent(type):
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        mro = cls.mro()
        client_annotations = {}
        # We want to skip objects in the heirachy from AzureApp and above, which should
        # only be 'object', but just in case that changes, we'll strip everything.
        for cls_type in mro[: mro.index(AzureApp) + 1]:
            for attr, annotation in get_annotations(cls_type).items():
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
                    # TODO: Currently this doesn't support other type hints like Union/Optional
                    client_annotations[attr] = annotation

                if attr in instance_kwargs:
                    continue
                try:
                    try:
                        instance_kwargs[attr] = kwargs.pop(attr)
                    except KeyError:
                        if (
                            attr in cls_type.__dict__
                            and isinstance(cls_type.__dict__[attr], ComponentField)
                            and cls_type.__dict__[attr].alias in kwargs
                        ):
                            instance_kwargs[attr] = kwargs.pop(cls_type.__dict__[attr].alias)
                        else:
                            instance_kwargs[attr] = getattr(cls_type, attr)
                    if attr in missing_kwargs:
                        missing_kwargs.pop(missing_kwargs.index(attr))
                except AttributeError:
                    missing_kwargs.append(attr)
        if kwargs:
            argument = "argument" if len(missing_kwargs) == 1 else "arguments"
            args = ", ".join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ", ".join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")

        # We pop these and pass explicitly because they need to be ordered first.
        config_store = instance_kwargs.pop("_config_store")
        closeables = instance_kwargs.pop("_closeables")
        return super().__call__(
            _config_store=config_store,
            _closeables=closeables,
            _client_annotations=client_annotations,
            **instance_kwargs,
        )


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
    _config_store: Mapping[str, Any] = field(alias="config_store", factory=dict, repr=False)
    _closeables: List[Union[SyncClient, AsyncClient]] = field(factory=list, init=False, repr=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        return cls(config_store=config_store, _infra=infra, **kwargs)

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
        attrs = []
        for attr in get_annotations(self.__class__):
            try:
                in_repr = self.__class__.__dict__[attr].repr
                if in_repr:
                    attrs.append(f"{attr}={repr(getattr(self, attr))}")
            except (KeyError, AttributeError):
                attrs.append(f"{attr}={repr(getattr(self, attr))}")
        repr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}({repr_str})"

    def __setattr__(self, name, value):
        if isinstance(value, Resource):
            kwargs = {}
            if isinstance(self.__class__.__dict__.get(name), ComponentField):
                kwargs = self.__class__.__dict__[name]._kwargs
            cls_type = get_annotations(self.__class__)[name]
            # TODO: Need to reduce the number of times get_annotations is called.
            value, credential = value.get_client(
                cls_type, config_store=self._config_store, return_credential=True, **kwargs
            )
            self._closeables.append(value)
            if credential not in self._closeables:
                self._closeables.append(credential)
        else:
            try:
                if callable(value.close) and value not in self._closeables:
                    # TODO: Confirm 'callable()' works for coroutines/
                    self._closeables.append(value)
            except AttributeError:
                pass
        return super().__setattr__(name, value)

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
        run_coroutine_sync(self.aclose())

    async def aclose(self) -> None:
        await asyncio.gather(*[self._close_client(c) for c in self._closeables])
