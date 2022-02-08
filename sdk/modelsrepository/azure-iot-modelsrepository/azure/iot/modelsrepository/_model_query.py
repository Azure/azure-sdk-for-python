# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import re
from typing import TYPE_CHECKING
from .dtmi_conventions import is_valid_dtmi
from ._common import ModelType, ModelProperties
from ._models import ModelMetadata

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Dict, List


class ModelQuery(object):
    def __init__(self, content):
        # type: (str) -> None
        """ The ModelQuery class is responsible for parsing DTDL v2 models to produce key metadata.
        In the current form ModelQuery is focused on determining model dependencies recursively
        via extends and component schemas.

        This class contains a partial parsing implementation that is strictly
        scoped for parsing dependencies. Ideally, this would be made obsolete by
        a full Python parser implementation, as it is supposed to be a single source
        of truth for the DTDL model specifications.

        Note that this implementation is not representative of what an eventual full
        parser implementation would necessarily look like from an API perspective

        :param content: JSON object representing the DTMI model
        :type content: JSON object
        """
        # Remove trailing commas if needed
        content = re.sub(r",[ \t\r\n]+}", "}", content.text())
        content = re.sub(r",[ \t\r\n]+\]", "]", content)
        self._content = content

    def parse_model(self):
        # type: () -> ModelMetadata
        return self._parse_interface(root=json.loads(self._content))

    def _parse_interface(self, root):
        # type: (Dict[str, Any]) -> ModelMetadata
        dtmi_id = root.get(ModelProperties.id.value)

        root_dtmi = dtmi_id if isinstance(dtmi_id, str) else None
        extends = self._parse_extends(root=root)
        components = self._parse_contents(root=root)

        return ModelMetadata(dtmi=root_dtmi, extends=extends, components=components)

    def _parse_extends(self, root):
        # type: (Dict[str, Any]) -> List[str | ModelMetadata]
        extends = root.get(ModelProperties.extends.value, None)
        return self._parse_component(component=extends)

    def _parse_contents(self, root):
        # type: (Dict[str, Any]) -> List[str | ModelMetadata]
        dependencies = set()
        contents = root.get(ModelProperties.contents.value, None)

        if isinstance(contents, list):
            for item in contents:
                dependencies.update(
                    self._parse_component(component=item.get(ModelProperties.schema.value))
                )
        return list(dependencies)

    def _parse_component(self, component):
        # type: (Any) -> List[str | ModelMetadata]
        dependencies = set()
        if isinstance(component, str) and is_valid_dtmi(component):
            dependencies.add(component)
        elif isinstance(component, list):
            # If it's a list, could have DTMIs or nested models
            for item in component:
                if isinstance(item, str):
                    # If there are strings in the list, that's a DTMI reference, so add it
                    dependencies.add(item)
                elif _is_interface_or_component(root=item):
                    # This is a nested model. Now go get its dependencies and add them
                    dependencies.update(self._parse_interface(root=item).dependencies)
        elif _is_interface_or_component(root=component):
            metadata = self._parse_interface(root=component).dependencies
            dependencies.update(metadata)
        return list(dependencies)

    def parse_models_from_list(self):
        # type: () -> Dict[str, str]
        """Parse contents from an expanded json using the ModelQuery class."""
        result = {}
        contents = json.loads(self._content)
        if isinstance(contents, list):
            for content in contents:
                model_metadata = ModelQuery(content=content).parse_model()
                result[model_metadata.dtmi] = content
        return result


def _is_interface_or_component(root):
    # type (Any) -> bool
    if not isinstance(root, dict):
        return False

    interface = root.get(ModelProperties.type.value)
    return (
        isinstance(interface, str) and
        interface in [ModelType.interface.value, ModelType.component.value]
    )
