# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import keyword
import types
from collections import ChainMap
from typing import (
    Dict,
    Generic,
    Mapping,
    Protocol,
    Any,
    Tuple,
    Union,
    Literal,
    Optional,
    List,
    Type,
    get_args,
    get_origin,
)
from typing_extensions import Self, TypeVar, dataclass_transform

from ._bicep.expressions import Parameter, MISSING, Default
from ._utils import run_coroutine_sync
from ._resource import Resource, SyncClient, AsyncClient
from .resources import RESOURCE_FROM_CLIENT_ANNOTATION
from .resources.resourcegroup import ResourceGroup
from .resources.managedidentity import UserAssignedIdentity
from .resources.appconfig import ConfigStore
from .resources.appservice.site import AppSite


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


def get_annotation_name(annotation: Any) -> str:
    # This is needed because in Python <3.10, the __name__ attribute is not set for
    # generic types. We need to get the name of the type from the string representation.
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    if str(annotation).startswith("typing.") and hasattr(annotation, "_name"):
        return annotation._name  # pylint: disable=protected-access
    annotation_name = str(annotation).rsplit(".", maxsplit=1)[-1]
    try:
        return annotation_name[0 : annotation_name.index("[")]
    except ValueError:
        return annotation_name


def get_mro_annotations(cls: Type, base_cls: Type) -> Mapping[str, Tuple[Any, Any]]:
    # TODO: Test if it's worth replacing this with typing.get_type_hints()
    # TODO: I don't think this supports string annotations. Need to test.
    mro = cls.mro()
    return {
        attr: (ann, t.__dict__.get(attr))
        for t in reversed(mro[: mro.index(base_cls) + 1])
        for attr, ann in get_annotations(t).items()
    }


def get_optional_annotation(annotation: Any) -> Optional[Type]:
    type_hint = get_origin(annotation)
    if type_hint is Union:
        union_args = get_args(annotation)
        if len(union_args) > 2 or union_args[1] is not type(None):
            raise TypeError(
                f"Unsupported type annotation: {annotation}. Only 'Optional' or 'Union' with None is supported."
            )
        return union_args[0]
    if type_hint is list:
        return None
    return annotation


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
        default_factory: Union[Literal[Default.MISSING], DefaultFactory, AsyncDefaultFactory],
        repr: bool,
        init: bool,
        alias: Optional[str],
        **kwargs,
    ):
        # TODO: make Parameter name optional?
        super().__init__("", default=default)
        self._default_factory = default_factory
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
        return self.name

    def __repr__(self) -> str:
        if self.default is not MISSING:
            return f"Field(default={repr(self.default)})"
        if self._default_factory is not MISSING:
            return f"Field(default={getattr(self._default_factory, '__name__', 'default_factory')}(**kwargs))"
        return "Field()"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name
        self._attrname = "_field__" + name

    async def _run_factory(self):
        factory = self._default_factory(**self.kwargs)
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
            if self._default_factory is not MISSING:
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
    default_factory=MISSING,
    repr=True,
    init=True,
    alias=None,
    **kwargs,
):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("Cannot specify both 'default' and 'factory'.")
    if alias and not init:
        raise ValueError("Alias is only supported if init=True.")
    return ComponentField(default=default, default_factory=default_factory, repr=repr, init=init, alias=alias, **kwargs)


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
    config_store: Optional[ConfigStore[Any]] = field(default=ConfigStore(), repr=False)
    host: Optional[AppSite] = field(default=None, repr=False)

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
    def __call__(cls, **kwargs):  # pylint: disable=too-many-statements
        instance_kwargs = {}
        missing_kwargs = []
        repr_objects = []
        dev_env = kwargs.pop("__dev_env", ChainMap())
        mro_annotations = kwargs.pop("__mro_annotations", None) or get_mro_annotations(cls, AzureApp)
        for attr, (annotation, attr_field) in mro_annotations.items():  # pylint: disable=too-many-nested-blocks
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
                    # already be processed by the time we get to any resources defined by the app.
                    client, credential = value.get_client(
                        annotation,
                        # We check both the local dev_env provided from load/provision and the provided
                        # config_store. We prioritize the latter because explicit > implicit.
                        config_store=dev_env,
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
                if attr == "config_store":
                    # We update the dev_env (used for creating clients) to include a user or infra
                    # provided config store.
                    dev_env = dev_env.new_child(instance_kwargs[attr])
                    # if annotation.__name__ == "Mapping":
                    # If the default config_store field type hint is used, we can update
                    # the instance config store to include the full dev_env. However
                    # if the user has chosen to overwrite the field with a different type
                    # (e.g. AppConfigurationProvider), we don't want to mess with that.
                    # instance_kwargs[attr] = dev_env
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


InfrastructureType = TypeVar("InfrastructureType", bound=AzureInfrastructure, default=AzureInfrastructure)


class AzureApp(Generic[InfrastructureType], metaclass=AzureAppComponent):
    # TODO: As these will have classattribute defaults, need to test behaviour
    # Might need to build a specifier object or use field
    _closeables: List[Union[SyncClient, AsyncClient]] = field(default_factory=list, init=False, repr=False)
    _repr_str: str = field(default="", init=False, repr=False)
    config_store: Mapping[str, Any] = field(default_factory=dict, repr=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @classmethod
    def load(
        cls, attr_map: Optional[Mapping[str, str]] = None, *, config_store: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Self:
        attr_map = attr_map or {}
        dev_env = kwargs.pop("__dev_env", None)
        # We only want to do this once per instance, so we'll pass it through to the metaclass.
        mro_annotations = kwargs.pop("__mro_annotations", None) or get_mro_annotations(cls, AzureApp)
        new_kwargs: Dict[str, Any] = {}
        for attr, (annotation, _) in mro_annotations.items():
            annotation = get_optional_annotation(annotation)
            if annotation and get_annotation_name(annotation) in RESOURCE_FROM_CLIENT_ANNOTATION:
                resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                new_kwargs[attr] = resource_cls(env_suffix=attr_map.get(attr))
            elif attr == "config_store":
                # We special case this one.
                # TODO: This is currently replacing any remote config store. Instead we should still
                # probably look for a remote store and combine them.
                if config_store:
                    new_kwargs[attr] = config_store
                else:
                    new_kwargs[attr] = ConfigStore()

        if dev_env is None:
            # We use a ChainMap here so that it can be added to the Infra ConfigStore resource in the
            # constructor purely during the client construction. This wont be persisted to the
            # app.config_store attribute. TODO: Should we? Probably no need as the dev env wont be present in
            # the deployment.
            # If there's a config_store in the infra, then that will ultimately be placed first in the chain.
            from ._provision import get_settings

            dev_env = ChainMap(get_settings())
        return cls(__dev_env=dev_env, __mro_annotations=mro_annotations, **new_kwargs)

    @classmethod
    def provision(
        cls,
        infra: Optional[InfrastructureType] = None,
        *,
        attr_map: Optional[Mapping[str, str]] = None,
        parameters: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Self:
        mro_annotations = get_mro_annotations(cls, AzureApp)
        from ._provision import provision

        if not infra:
            try:
                from infra import build_infra  # type: ignore[import]

                infra = build_infra()
            except ImportError:
                attr_map = {}
                fields = []
                for attr, (annotation, _) in mro_annotations.items():
                    annotation = get_optional_annotation(annotation)
                    if annotation and get_annotation_name(annotation) in RESOURCE_FROM_CLIENT_ANNOTATION:
                        resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                        attr_map[attr] = attr
                        fields.append((attr, resource_cls, field(default=resource_cls())))
                    elif attr == "config_store":
                        # We special case this one.
                        # TODO: Pretty sure this shouldn't be in the attr_map
                        pass
                dev_env = provision(make_infra(cls.__name__, fields)(), parameters=parameters, **kwargs)
        else:
            dev_env = provision(infra, parameters=parameters, **kwargs)
        # The dev env returned here is a ChainMap of the deployed settings along with the user
        # provided parameters. If there's a config_store provided with the infra deployment, this
        # will be added to the front of the chain.
        return cls.load(attr_map=attr_map, __dev_env=dev_env, __mro_annotations=mro_annotations)

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
        # from a field default or default_factory, it is assumed that we don't own it.
        run_coroutine_sync(self.aclose())

    async def aclose(self) -> None:
        # This would be more efficient if we used something like asyncio.gather, but that would
        # exclude trio compatibility, and would prefer to avoid dependency on anyio.
        for closeable in self._closeables:
            await self._close_client(closeable)
