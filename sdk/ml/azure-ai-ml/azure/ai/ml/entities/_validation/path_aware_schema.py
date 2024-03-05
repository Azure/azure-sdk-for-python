# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import typing
from os import PathLike
from pathlib import Path

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from ..._schema import PathAwareSchema
from .._job.pipeline._attr_dict import try_get_non_arbitrary_attr
from .._util import convert_ordered_dict_to_dict
from .schema import SchemaValidatableMixin


class PathAwareSchemaValidatableMixin(SchemaValidatableMixin):
    """The mixin class for schema validation. Entity classes inheriting from this class should have a base path
    and a schema of PathAwareSchema.
    """

    @property
    def __base_path_for_validation(self) -> typing.Union[str, PathLike]:
        """Get the base path of the resource.

        It will try to return self.base_path, then self._base_path, then Path.cwd() if above attrs are non-existent or
        `None.

        :return: The base path of the resource
        :rtype: typing.Union[str, os.PathLike]
        """
        return (
            try_get_non_arbitrary_attr(self, BASE_PATH_CONTEXT_KEY)
            or try_get_non_arbitrary_attr(self, f"_{BASE_PATH_CONTEXT_KEY}")
            or Path.cwd()
        )

    def _default_context(self) -> dict:
        # Note that, although context can be passed, nested.schema will be initialized only once
        # base_path works well because it's fixed after loaded
        return {BASE_PATH_CONTEXT_KEY: self.__base_path_for_validation}

    @classmethod
    def _create_schema_for_validation(cls, context: typing.Any) -> PathAwareSchema:
        raise NotImplementedError()

    @classmethod
    def _create_validation_error(cls, message: str, no_personal_data_message: str) -> Exception:
        raise NotImplementedError()

    def _dump_for_validation(self) -> typing.Dict:
        # this is not a necessary step but to keep the same behavior as before
        # empty items will be removed when converting to dict
        return typing.cast(dict, convert_ordered_dict_to_dict(super()._dump_for_validation()))
