from dataclasses import dataclass
from typing import Any, Optional, Union
import pytest

from azure.projects._resource import ResourceReference
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.storage.blobs.container import BlobContainer
from azure.projects import Parameter, AzureApp, AzureInfrastructure, field, MISSING


def test_component_infra_invalid(): ...


#     TODO
#     test bad type hint string
#     with pytest.raises(RuntimeError):
#         class Foo:
#             test = resource()

#     with pytest.raises(RuntimeError):
#         class Foo:
#             test: int = resource()

#     with pytest.raises(ValueError):
#         class Foo:
#             test: BlobStorage = resource(default=BlobStorage(), default_factory=BlobStorage)

#     class Foo:
#         test: BlobStorage = resource(default_factory=BlobStorage)

#     foo = Foo()
#     with pytest.raises(TypeError):
#         foo.test = 3
#     with pytest.raises(TypeError):
#         foo.test = BlobContainer()


def test_component_infra_inheritance():
    class InfraA(AzureInfrastructure):
        storage: BlobStorage

    with pytest.raises(TypeError):
        InfraA()

    class InfraB(InfraA):
        storage: BlobStorage = BlobStorage()

    assert InfraB()

    class InfraC(InfraA):
        data: BlobContainer

    with pytest.raises(TypeError):
        InfraC()

    class InfraD(AzureInfrastructure):
        resource_group: ResourceGroup = field()

    with pytest.raises(TypeError):
        InfraD()


# TODO: Test linked infra with different RG, identity, config
def test_component_infra_linked():
    class InfraA(AzureInfrastructure):
        storage: BlobStorage = field()
        storage_2: BlobStorage = BlobStorage(account="Foo")

    class InfraB(AzureInfrastructure):
        data: BlobStorage = field()
        component: InfraA = InfraA(storage=data)
        component_2: InfraA = InfraA(storage=component.storage_2, storage_2=component.storage)

    infra = InfraB(data=BlobStorage(account="bar"))
    assert infra.data == BlobStorage(account="bar")
    assert infra.component.storage == BlobStorage(account="bar")
    assert infra.component.storage_2 == BlobStorage(account="Foo")
    assert infra.component_2.storage == BlobStorage(account="Foo")
    assert infra.component_2.storage_2 == BlobStorage(account="bar")


def test_component_infra_attr_references():
    with pytest.raises(NameError):

        class Infra(AzureInfrastructure):
            storage: BlobStorage
            data: BlobContainer = BlobContainer(account=storage)

    class Infra(AzureInfrastructure):
        name: str = "foo"
        storage: BlobStorage = BlobStorage.reference(account=name)
        data: BlobContainer = BlobContainer(account=storage)

    infra = Infra()
    assert infra.data == BlobContainer(account=BlobStorage.reference(account="foo"))

    class Infra(AzureInfrastructure):
        name: str = field()
        storage: BlobStorage = BlobStorage.reference(account=name)
        data: BlobContainer = BlobContainer(account=storage)

    infra = Infra(name="bar")
    assert infra.storage.parent.properties.get("name").get(infra) == "bar"
    assert infra.data.parent.parent.properties.get("name").get(infra) == "bar"

    class Infra(AzureInfrastructure):
        storage: BlobStorage = field()
        data: BlobContainer = BlobContainer(account=storage)

    infra = Infra(storage=BlobStorage.reference(account="foo"))
    # TODO: How to unravel this???
    assert infra.data.parent.parent.properties.get("name").get(infra) == BlobStorage(account="foo")


def test_component_infra_repr(): ...
def test_component_infra_init():
    # TODO
    ...


def test_component_infra_factory(): ...
def test_component_infra_alias():
    # TODO
    ...


def test_component_infra_basic():

    class Infra(AzureInfrastructure):
        test: BlobStorage = field()

    with pytest.raises(TypeError):
        Infra()

    with pytest.raises(TypeError):
        Infra(foo="bar")

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: BlobStorage = field(default=MISSING)

    with pytest.raises(TypeError):
        Infra()

    with pytest.raises(TypeError):
        Infra(foo="bar")

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: BlobStorage

    with pytest.raises(TypeError):
        Infra()

    with pytest.raises(TypeError):
        Infra(foo="bar")

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: BlobStorage = field(default=BlobStorage(account="test"))

    infra = Infra()
    assert infra.test == BlobStorage(account="test")
    assert infra.test.parent == StorageAccount(name="test")

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: BlobStorage[Any] = BlobStorage(account="test")

    infra = Infra()
    assert infra.test == BlobStorage(account="test")
    assert infra.test.parent == StorageAccount(name="test")
    with pytest.raises(AttributeError):
        infra.test = BlobStorage.reference(account="existing")
    with pytest.raises(AttributeError):
        infra.test = "a string"

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: Optional[BlobStorage] = None

    infra = Infra()
    assert infra.test == None

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: Optional[BlobStorage] = field(default=None)

    infra = Infra()
    assert infra.test == None

    infra = Infra(test=BlobStorage(account="foo"))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: BlobStorage[ResourceReference]

    with pytest.raises(TypeError):
        Infra()

    infra = Infra(test=BlobStorage.reference(account=StorageAccount.reference(name="foo")))
    assert infra.test == BlobStorage(account="foo")
    assert infra.test.parent == StorageAccount(name="foo")

    class Infra(AzureInfrastructure):
        test: Union[BlobContainer, BlobStorage] = BlobContainer(name="data", account="data")

    infra = Infra()
    assert infra.test == BlobContainer(name="data", account="data")
    assert infra.test.parent == BlobStorage(account="data")
    assert infra.test.parent.parent == StorageAccount(name="data")


def test_component_infra_hybrid():
    class TestInfra(AzureInfrastructure):
        number: int
        resource: BlobContainer
        string: str = "teststring"
        another_resource: BlobStorage = field(default=BlobStorage(), repr=False)
        data: dict = field(default_factory=dict, repr=False, foo=string, bar=another_resource)

        def some_func(self) -> str:
            return self.string

    with pytest.raises(TypeError):
        TestInfra()

    infra = TestInfra(number=7, resource=BlobContainer.reference(name="A", account="B"))
    assert infra.number == 7
    assert infra.string == "teststring"
    assert infra.some_func() == "teststring"
    assert infra.resource == BlobContainer(name="A", account="B")
    assert infra.another_resource == BlobStorage()
    assert infra.data["bar"].get(infra) == BlobStorage()
    assert infra.data["foo"] == "teststring"
    assert repr(infra) == "TestInfra(number=7, resource=BlobContainer('A'), string='teststring')"


def test_component_infra_export_config():
    # TODO: Test ComponentFields as parameters
    ...
