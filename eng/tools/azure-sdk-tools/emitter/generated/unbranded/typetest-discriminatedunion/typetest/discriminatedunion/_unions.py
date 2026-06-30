# coding=utf-8

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import models as _models
PetWithEnvelope = Union["_models.Cat", "_models.Dog"]
PetWithCustomNames = Union["_models.Cat", "_models.Dog"]
PetInline = Union["_models.Cat", "_models.Dog"]
PetInlineWithCustomDiscriminator = Union["_models.Cat", "_models.Dog"]
