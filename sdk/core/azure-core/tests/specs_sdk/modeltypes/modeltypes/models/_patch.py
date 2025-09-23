# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, BinaryIO, Dict, Any, Optional
from datetime import date, datetime, time, timedelta, tzinfo
from .._utils.model_base import Model as HybridModel, rest_field
from .._utils.serialization import Model as MsrestModel


class HybridPet(HybridModel):
    name: str = rest_field()  # my name
    species: str = rest_field()  # my species


class HybridDog(HybridPet):
    breed: str = rest_field()
    is_best_boy: bool = rest_field(name="isBestBoy")


class MsrestPet(MsrestModel):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "species": {"key": "species", "type": "str"},
    }

    def __init__(self, *, name: str = None, species: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.species = species


class MsrestDog(MsrestPet):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "species": {"key": "species", "type": "str"},
        "breed": {"key": "breed", "type": "str"},
        "is_best_boy": {"key": "isBestBoy", "type": "bool"},
    }

    def __init__(self, *, name: str, species: str, breed: str, is_best_boy: bool, **kwargs):
        super().__init__(id=id, type=type, name=name, species=species, **kwargs)
        self.breed = breed
        self.is_best_boy = is_best_boy


class HybridAddress(HybridModel):
    street: str = rest_field()
    city: str = rest_field()
    zip_code: str = rest_field(name="zipCode")


class HybridPerson(HybridModel):
    name: str = rest_field()
    home_address: HybridAddress = rest_field(name="homeAddress")
    work_address: HybridAddress = rest_field(name="workAddress")


class HybridContactInfo(HybridModel):
    email: str = rest_field()
    phone: str = rest_field()
    addresses: List[HybridAddress] = rest_field()


class HybridDepartment(HybridModel):
    name: str = rest_field()
    cost_center: str = rest_field(name="costCenter")


class HybridEmployee(HybridModel):
    employee_id: str = rest_field(name="employeeId", visibility=["read"])
    first_name: str = rest_field(name="firstName")
    last_name: str = rest_field(name="lastName")
    hire_date: date = rest_field(name="hireDate")
    contact: HybridContactInfo = rest_field()
    department: HybridDepartment = rest_field()
    skills: List[str] = rest_field()
    performance_ratings: dict[str, float] = rest_field(name="performanceRatings")


class MsrestAddress(MsrestModel):
    _attribute_map = {
        "street": {"key": "street", "type": "str"},
        "city": {"key": "city", "type": "str"},
        "zip_code": {"key": "zipCode", "type": "str"},
    }

    def __init__(self, *, street: str, city: str, zip_code: str, **kwargs):
        super().__init__(**kwargs)
        self.street = street
        self.city = city
        self.zip_code = zip_code


class MsrestPerson(MsrestModel):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "home_address": {"key": "homeAddress", "type": "MsrestAddress"},
        "work_address": {"key": "workAddress", "type": "MsrestAddress"},
    }

    def __init__(self, *, name: str, home_address: MsrestAddress, work_address: MsrestAddress, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.home_address = home_address
        self.work_address = work_address


class MsrestContactInfo(MsrestModel):
    _attribute_map = {
        "email": {"key": "email", "type": "str"},
        "phone": {"key": "phone", "type": "str"},
        "addresses": {"key": "addresses", "type": "[MsrestAddress]"},
    }

    def __init__(self, *, email: str, phone: str, addresses: List[MsrestAddress], **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.phone = phone
        self.addresses = addresses


class MsrestDepartment(MsrestModel):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "cost_center": {"key": "costCenter", "type": "str"},
    }

    def __init__(self, *, name: str, cost_center: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.cost_center = cost_center


class MsrestEmployee(MsrestModel):

    _validation = {
        "employee_id": {"readonly": True},
    }
    _attribute_map = {
        "employee_id": {"key": "employeeId", "type": "str"},
        "first_name": {"key": "firstName", "type": "str"},
        "last_name": {"key": "lastName", "type": "str"},
        "hire_date": {"key": "hireDate", "type": "date"},
        "contact": {"key": "contact", "type": "MsrestContactInfo"},
        "department": {"key": "department", "type": "MsrestDepartment"},
        "skills": {"key": "skills", "type": "[str]"},
        "performance_ratings": {"key": "performanceRatings", "type": "{str: float}"},
    }

    def __init__(
        self,
        *,
        employee_id: str,
        first_name: str,
        last_name: str,
        hire_date: date,
        contact: MsrestContactInfo,
        department: MsrestDepartment,
        skills: List[str],
        performance_ratings: Dict[str, float],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.hire_date = hire_date
        self.contact = contact
        self.department = department
        self.skills = skills
        self.performance_ratings = performance_ratings


class HybridProduct(HybridModel):
    product_id: str = rest_field(name="productId")
    product_name: str = rest_field(name="ProductName")  # Casing difference
    unit_price: float = rest_field(name="unit-price")  # Dash in REST name
    stock_count: int = rest_field(name="stock_count")  # Underscore in both


class MsrestProduct(MsrestModel):
    _attribute_map = {
        "product_id": {"key": "productId", "type": "str"},
        "product_name": {"key": "ProductName", "type": "str"},  # Casing difference
        "unit_price": {"key": "unit-price", "type": "float"},  # Dash in REST name
        "stock_count": {"key": "stock_count", "type": "int"},  # Underscore in both
    }


class HybridEvent(HybridModel):
    event_id: str = rest_field(name="eventId")
    start_time: datetime = rest_field(name="startTime")
    end_time: datetime = rest_field(name="endTime")
    created_date: date = rest_field(name="createdDate", format="date")
    reminder_time: time = rest_field(name="reminderTime", format="time")
    duration: timedelta = rest_field(format="duration")


class MsrestEvent(MsrestModel):
    _attribute_map = {
        "event_id": {"key": "eventId", "type": "str"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "created_date": {"key": "createdDate", "type": "date"},
        "reminder_time": {"key": "reminderTime", "type": "time"},
        "duration": {"key": "duration", "type": "duration"},
    }

    def __init__(
        self,
        *,
        event_id: str,
        start_time: datetime,
        end_time: datetime,
        created_date: date,
        reminder_time: time,
        duration: timedelta,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.event_id = event_id
        self.start_time = start_time
        self.end_time = end_time
        self.created_date = created_date
        self.reminder_time = reminder_time
        self.duration = duration


class HybridResource(HybridModel):
    id: str = rest_field(visibility=["read"])  # Readonly
    name: str = rest_field()
    description: str = rest_field()


class MsrestResource(MsrestModel):
    _validation = {
        "id": {"readonly": True},
    }
    _attribute_map = {
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
    }

    def __init__(self, *, name: str, description: str, **kwargs):
        super().__init__(**kwargs)
        self.id: Optional[str] = None
        self.name = name
        self.description = description


class HybridTag(HybridModel):
    key: str = rest_field()
    value: str = rest_field()


class HybridTaggedResource(HybridModel):
    name: str = rest_field()
    tags: list[HybridTag] = rest_field()
    metadata: dict[str, str] = rest_field()
    string_list: list[str] = rest_field(name="stringList")
    int_list: list[int] = rest_field(name="intList")


class MsrestTag(MsrestModel):
    _attribute_map = {
        "key": {"key": "key", "type": "str"},
        "value": {"key": "value", "type": "str"},
    }

    def __init__(self, *, key: str, value: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value


class MsrestTaggedResource(MsrestModel):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "tags": {"key": "tags", "type": "[MsrestTag]"},
        "metadata": {"key": "metadata", "type": "{str}"},
        "string_list": {"key": "stringList", "type": "[str]"},
        "int_list": {"key": "intList", "type": "[int]"},
    }

    def __init__(
        self,
        *,
        name: str,
        tags: List[MsrestTag],
        metadata: Dict[str, str],
        string_list: List[str],
        int_list: List[int],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.tags = tags
        self.metadata = metadata
        self.string_list = string_list
        self.int_list = int_list


class FileUpload(HybridModel):
    name: str = rest_field()
    content: BinaryIO = rest_field(is_multipart_file_input=True)
    content_type: str = rest_field(name="contentType")


class HybridOptionalProps(HybridModel):
    required_prop: str = rest_field()
    optional_prop: Optional[str] = rest_field(name="optionalProp")
    optional_model: Optional["HybridOptionalProps"] = rest_field(name="optionalModel")


class MsrestOptionalProps(MsrestModel):
    _attribute_map = {
        "required_prop": {"key": "requiredProp", "type": "str"},
        "optional_prop": {"key": "optionalProp", "type": "str"},
        "optional_model": {"key": "optionalModel", "type": "HybridOptionalProps"},
    }

    def __init__(
        self,
        *,
        required_prop: str,
        optional_prop: Optional[str] = None,
        optional_model: Optional["HybridOptionalProps"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.required_prop = required_prop
        self.optional_prop = optional_prop
        self.optional_model = optional_model


class MsrestFlattenModel(MsrestModel):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "description": {"key": "properties.modelDescription", "type": "str"},
        "age": {"key": "properties.age", "type": "int"},
    }

    def __init__(self, *, name: str, description: str, age: int, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.age = age


class HybridPetAPTrue(HybridModel):
    name: str = rest_field()


class MsrestPetAPTrue(MsrestModel):
    _attribute_map = {
        "additional_properties": {"key": "", "type": "{object}"},
        "name": {"key": "name", "type": "str"},
    }

    def __init__(self, *, additional_properties: Optional[Dict[str, Any]], name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.additional_properties = additional_properties
        self.name = name


class MsrestClientNameAndJsonEncodedNameModel(MsrestModel):
    _attribute_map = {
        "client_name": {"key": "wireName", "type": "str"},
    }

    def __init__(self, *, client_name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client_name = client_name


class MsrestReadonlyModel(MsrestModel):
    _validation = {
        "id": {"readonly": True},
    }
    _attribute_map = {
        "id": {"key": "readonlyProp", "type": "str"},
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id: Optional[str] = None


__all__: List[str] = [
    "HybridPet",
    "HybridDog",
    "MsrestPet",
    "MsrestDog",
    "HybridAddress",
    "HybridPerson",
    "HybridContactInfo",
    "HybridDepartment",
    "HybridEmployee",
    "MsrestAddress",
    "MsrestPerson",
    "MsrestContactInfo",
    "MsrestDepartment",
    "MsrestEmployee",
    "HybridProduct",
    "MsrestProduct",
    "HybridEvent",
    "MsrestEvent",
    "HybridResource",
    "MsrestResource",
    "HybridTag",
    "HybridTaggedResource",
    "MsrestTag",
    "MsrestTaggedResource",
    "FileUpload",
    "HybridOptionalProps",
    "MsrestOptionalProps",
    "MsrestFlattenModel",
    "HybridPetAPTrue",
    "MsrestPetAPTrue",
    "MsrestClientNameAndJsonEncodedNameModel",
    "MsrestReadonlyModel",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
