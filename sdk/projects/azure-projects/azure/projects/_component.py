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
    TYPE_CHECKING,
    Coroutine,
    Generic,
    Mapping,
    Protocol,
    TypeVar,
    Any,
    Union,
    Literal,
    Optional,
    List,
    Type
)
from typing_extensions import Self, dataclass_transform

from ._bicep.expressions import Parameter, MISSING, Default, ParameterType
from ._resource import Resource, _load_dev_environment, ResourceReference
from .resources import ResourceIdentifiers, RESOURCE_FROM_CLIENT_ANNOTATION
from .resources.resourcegroup import ResourceGroup
from .resources.managedidentity import UserAssignedIdentity

if TYPE_CHECKING:
    from .resources.resourcegroup.types import ResourceGroupResource
    from .resources.managedidentity.types import UserAssignedIdentityResource


def get_annotations(cls: Type) -> Mapping[str, Any]:
    """This is needed for Python <3.10"""
    try:
        from inspect import get_annotations
        return get_annotations(cls)
    except ImportError:
        pass
    try:
        return cls.__annotations__
    except AttributeError:
        pass
    return {}


class DefaultFactory(Protocol, Generic[ParameterType]):
    def __call__(self, **kwargs) -> ParameterType:
        ...
class ResourceFactory(Protocol):
    def __call__(self, **kwargs) -> Resource:
        ...


class ComponentField(Parameter[ParameterType]):
    def __init__(
            self,
            *,
            default: ParameterType,
            factory: Union[Literal[Default.MISSING], DefaultFactory[ParameterType]],
            repr: bool,
            init: bool,
            alias: Optional[str],
            **kwargs
    ):
        self._factory = factory
        self._kwargs = kwargs
        self._default = default
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None
        self._name: Optional[str] = None
        self.repr = repr
        self.init = init
        self.alias = alias
        self.module = "main"  # TODO: refactor this away

    @property
    def name(self) -> str:
        if not self._owner or not self._name:
            raise ValueError("ComponentField not used in component class.")
        return f"{self._owner.__name__}.{self._name}"

    @property
    def default(self) -> Any:
        return self._default   
        
    def __repr__(self) -> str:
        if self._default is not MISSING:
            return f"ComponentField(default={repr(self._default)})"
        if self._factory is not MISSING:
            return f"ComponentField(default={self._factory.__name__}(**kwargs))"
        return "ComponentField()"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name
        self._attrname = '_field__' + name
        try:
            self._type = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"'{owner.__name__}.{name}' is missing type hint.") from None

    def __get__(self, obj, obj_type) -> ParameterType:
        if obj is None:
            if self._default is not MISSING:
                return self._default
            if self._factory is not MISSING:
                return self._factory(**self._kwargs)
            raise AttributeError(f"No default value provided for '{self._owner.__name__}.{self._name}'.")
        return getattr(obj, self._attrname)

    def __set__(self, obj: 'AzureInfrastructure', value: ParameterType):
        setattr(obj, self._attrname, value)

    def get(self, obj: Optional['AzureInfrastructure'] = None, /) -> ParameterType:
        return self.__get__(obj, obj.__class__)


def field(
        *,
        default: Union[Any, Literal[Default.MISSING]] = MISSING,
        factory: Union[DefaultFactory, Literal[Default.MISSING]] = MISSING,
        repr: bool = True,
        # init: bool = True,
        alias: Optional[str] = None,
        **kwargs
) -> ComponentField:
    if default is not MISSING and factory is not MISSING:
        raise ValueError("Cannot specify both 'default' and 'factory'.")
    return ComponentField(
        default=default,
        factory=factory,
        repr=repr,
        init=True,
        alias=alias,
        **kwargs
    )


def _parameter(*, default = None, default_factory = None, **kwargs):
    # TODO not sure how we should handle this yet
    if default:
        return default
    if default_factory:
        return default_factory()
    return None


@dataclass_transform(field_specifiers=(field, _parameter), kw_only_default=True)
class AzureInfraComponent(type):
    # TODO: The typing of the __call__ function is breaking
    # typing when kwargs are passed into the constructor.
    # Need to figure that out.....
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        child_infra_components: List[AzureInfrastructure] = []
        mro = cls.mro()
        # We want to skip objects in the heirachy above AzureInfrastructure, which should
        # only be 'object', but just in case that changes, we'll strip everything.
        for cls_type in mro[:mro.index(AzureInfrastructure) + 1]:
            for attr in get_annotations(cls_type):
                if attr in instance_kwargs:
                    continue
                try:
                    try:
                        instance_kwargs[attr] = kwargs.pop(attr)
                    except KeyError:
                        if attr in cls.__dict__ and isinstance(cls.__dict__[attr], ComponentField) and cls.__dict__[attr].alias in kwargs:
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
            args = ', '.join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ', '.join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")
        kwargs.update(instance_kwargs)
        # Because the order of resources is important, we always want to make
        # 'resource_group' and 'identity' first.
        resource_group = kwargs.pop('resource_group')
        identity=kwargs.pop('identity')
        value = super().__call__(resource_group=resource_group, identity=identity, **kwargs)
        # This is used for internal linking of infra components, it should only matter if infra components
        # are instantiated in a field default.
        for infra_instance in child_infra_components:
            infra_instance._parent = value
        return value


class AzureInfrastructure(metaclass=AzureInfraComponent):
    _parent: Optional['AzureInfrastructure'] = None
    resource_group: ResourceGroup = field(default=ResourceGroup(), repr=False)
    identity: Optional[UserAssignedIdentity] = field(default=UserAssignedIdentity(), repr=False)

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


def make_infra(cls_name, fields, *, bases=(), namespace=None, module=None) -> Type[AzureInfrastructure]:
    """This code is taken from stdlib dataclasses.make_dataclass"""
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
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifiers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        annotations[name] = tp

    # Update 'ns' with the user-supplied namespace plus our calculated values.
    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns['__annotations__'] = annotations

    # We use `types.new_class()` instead of simply `type()` to allow dynamic creation
    # of generic dataclasses.
    cls = types.new_class(cls_name, bases, {}, exec_body_callback)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the dataclass is created.
    if module is None:
        try:
            module = sys._getframemodulename(1) or '__main__'
        except AttributeError:
            try:
                module = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass
    if module is not None:
        cls.__module__ = module
    return cls


@dataclass_transform(field_specifiers=(_parameter, field), kw_only_default=True)
class AzureAppComponent(type):
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        instance_kwargs['env_name'] = kwargs.pop('env_name', None)
        if instance_kwargs['env_name']:
            instance_kwargs['config_store'] = kwargs.pop('config_store', None)
            if instance_kwargs['config_store'] is not None:
                raise ValueError("Cannot specify both 'env_name' and 'config_store'.")
            instance_kwargs['config_store'] = _load_dev_environment(instance_kwargs['env_name'])
        else:
            instance_kwargs['config_store'] = kwargs.pop('config_store', {})
        missing_kwargs = []
        mro = cls.mro()
        client_annotations = {}
        # We want to skip objects in the heirachy from AzureApp and above, which should
        # only be 'object', but just in case that changes, we'll strip everything.
        for cls_type in mro[:mro.index(AzureApp)]:
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
                        if attr in cls.__dict__ and isinstance(cls.__dict__[attr], ComponentField) and cls.__dict__[attr].alias in kwargs:
                            instance_kwargs[attr] = kwargs.pop(cls.__dict__[attr].alias)
                        else:
                            instance_kwargs[attr] = getattr(cls, attr)
                    if attr in missing_kwargs:
                        missing_kwargs.pop(missing_kwargs.index(attr))
                except AttributeError:
                    missing_kwargs.append(attr)
        if kwargs:
            argument = "argument" if len(missing_kwargs) == 1 else "arguments"
            args = ', '.join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            missing = set(missing_kwargs)
            argument = "argument" if len(missing) == 1 else "arguments"
            attrs = ', '.join([f"'{attr}'" for attr in missing])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")
        instance_kwargs['_client_annotations'] = client_annotations
        return super().__call__(**instance_kwargs)


T = TypeVar("T")
def run_coroutine_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    """TODO: Found this on StackOverflow - needs further inspection
    https://stackoverflow.com/questions/55647753/call-async-function-from-sync-function-while-the-synchronous-function-continues
    """
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
        else:
            with ThreadPoolExecutor() as pool:
                future = pool.submit(run_in_new_loop)
                return future.result(timeout=timeout)
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()


class AzureApp(metaclass=AzureAppComponent):
    # TODO: As these will have classattribute defaults, need to test behaviour
    # Might need to build a specifier object or use field
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)
    _env_name: Optional[str] = _parameter(alias="env_name", default=None) # TODO: Remove

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store')
        self._env_name = kwargs.pop('env_name')
        self._client_annotations = kwargs.pop('_client_annotations')
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def load(
        cls,
        infra: Optional[AzureInfrastructure] = None,
        attr_map: Optional[Mapping[str, str]] = None,
        /,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None
    ) -> Self:
        if attr_map and not infra:
            raise ValueError('Cannot specify attr_map without providing infrastructure object.')
        attr_map = attr_map or {}
        if not infra:
            env_name = env_name or cls.__name__
            fields = []
            for attr, annotation in get_annotations(cls).items():
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
                    resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                    attr_map[attr] = attr
                    fields.append((attr, resource_cls, field(default=resource_cls())))
            infra = make_infra(f"_{cls.__name__}Infra", fields)
        if attr_map:
            kwargs = {c_attr: getattr(infra, i_attr) for c_attr, i_attr in attr_map.items()}
        else:
            infra_resources = {r.identifier: r for r in infra.__dict__.values() if isinstance(r, Resource)}
            kwargs = {}
            for attr, annotation in get_annotations(cls).items():
                # TODO: Duplicate annotation traversal - needs revising
                # TODO: Currently this doesn't support other type hints like Union/Optional
                # TODO: This doesn't support alias
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION and RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__] in infra_resources:
                    kwargs[attr] = infra_resources[RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__]]

        if config_store is None and not env_name:
            env_name = infra.__class__.__name__
        return cls(config_store=config_store, env_name=env_name, **kwargs)

    @classmethod
    def provision(
        cls,
        infra: Optional[AzureInfrastructure] = None,
        attr_map: Optional[Mapping[str, str]] = None,
        /,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
        **kwargs
    ) -> Self:
        if attr_map and not infra:
            raise ValueError('Cannot specify attr_map without providing infrastructure object.')
        from ._provision import provision
        if not infra:
            env_name = env_name or cls.__name__
            attr_map = {}
            fields = []
            for attr, annotation in get_annotations(cls).items():
                if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
                    resource_cls = RESOURCE_FROM_CLIENT_ANNOTATION[annotation.__name__].resource()
                    attr_map[attr] = attr
                    fields.append((attr, resource_cls, field(default=resource_cls())))
            infra = make_infra(env_name, fields)()
        provision(infra, config_store=config_store, name=env_name, **kwargs)
        return cls.load(infra, attr_map, config_store=config_store, env_name=env_name)

    def __setattr__(self, name, value):
        if name.startswith('_field__') or name in ['_config_store', '_env_name', '_client_annotations']:
            return super().__setattr__(name, value)
        if isinstance(value, Resource):
            kwargs = {}
            if isinstance(self.__class__.__dict__.get(name), ComponentField):
                kwargs = self.__class__.__dict__[name]._kwargs
            cls_type = get_annotations(self.__class__)[name]
            # TODO: Need to reduce the number of times get_annotations is called.
            value = value.get_client(cls_type, config_store=self._config_store, **kwargs)
        return super().__setattr__(name, value)
    
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.aclose()

    async def _close_client(self, client) -> None:
        try:
            closer = client.close()
        except (AttributeError, TypeError):
            return
        try:
            await closer
        except TypeError:
            pass

    def close(self) -> None:
        run_coroutine_sync(self.aclose())

    async def aclose(self) -> None:
        await asyncio.gather(*[self._close_client(c) for c in self.__dict__.values()])
