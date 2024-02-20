# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Dict, Optional, Union

from marshmallow import Schema

from azure.ai.ml._schema.component.import_component import ImportComponentSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType

from ..._schema import PathAwareSchema
from ..._utils.utils import parse_args_description_from_docstring
from .._util import convert_ordered_dict_to_dict
from .component import Component


class ImportComponent(Component):
    """Import component version, used to define an import component.

    :param name: Name of the component.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param description: Description of the component.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param source: Input source parameters of the component.
    :type source: dict
    :param output: Output of the component.
    :type output: dict
    :param is_deterministic: Whether the command component is deterministic. Defaults to True.
    :type is_deterministic: bool
    :param kwargs: Additional parameters for the import component.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        display_name: Optional[str] = None,
        source: Optional[Dict] = None,
        output: Optional[Dict] = None,
        is_deterministic: bool = True,
        **kwargs,
    ) -> None:
        kwargs[COMPONENT_TYPE] = NodeType.IMPORT
        # Set default base path
        if BASE_PATH_CONTEXT_KEY not in kwargs:
            kwargs[BASE_PATH_CONTEXT_KEY] = Path(".")

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=source,
            outputs={"output": output} if output else None,
            is_deterministic=is_deterministic,
            **kwargs,
        )

        self.source = source
        self.output = output

    def _to_dict(self) -> Dict:
        return convert_ordered_dict_to_dict({**self._other_parameter, **super(ImportComponent, self)._to_dict()})

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return ImportComponentSchema(context=context)

    @classmethod
    def _parse_args_description_from_docstring(cls, docstring):
        return parse_args_description_from_docstring(docstring)

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(ImportComponent, self).__str__()
