# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains a partial parsing implementation that is strictly
scoped for parsing dependencies. Ideally, this would be made obsolete by
a full Python parser implementation, as it is supposed to be a single source
of truth for the DTDL model specifications.

Note that this implementation is not representative of what an eventual full
parser implementation would necessarily look like from an API perspective
"""
import logging
from six import text_type
from .dtmi_conventions import is_valid_dtmi
from ._common import ModelType, ModelProperties

_LOGGER = logging.getLogger(__name__)

class Model(object):
    def __init__(
        self,
        dtmi="",
        extends=None,
        components=None,
        contents=None,
    ):
        """ The Model class is responsible for storing results from ModelQuery.parse_model().

        :param dtmi: The DTMI for the model
        :type dtmi: str
        :param extends: The list of strings or models representing the extend
        :type extends: list[str], list[Model]
        :param components: The list of strings or models representing the components
        :type components: list[str], list[Model]
        :param contents: The raw data representing the model
        :type contents: dict
        """
        self.dtmi = dtmi
        self.extends = extends if extends else []
        self.components = components if components else []
        self.dependencies = list(set(extends).union(set(components)))
        self.contents = contents

    def __repr__(self):
        return self.contents


class ModelQuery(object):
    def __init__(self, content):
        """ The ModelQuery class is responsible for parsing DTDL v2 models to produce key metadata.
        In the current form ModelQuery is focused on determining model dependencies recursively
        via extends and component schemas.

        :param content: JSON object representing the DTMI model
        :type content: JSON object
        """
        self._content = content

    def parse_model(self):
        return self._parse_interface(self._content)

    def _parse_interface(self, root):
        dtmi_id = root.get(ModelProperties.id.value)

        root_dtmi = dtmi_id if isinstance(dtmi_id, text_type) else None
        extends = self._parse_extends(root)
        contents = self._parse_contents(root)

        return Model(root_dtmi, extends, contents)

    def _parse_extends(self, root):
        extends = root.get(ModelProperties.extends.value, None)
        return self._parse_component(extends)

    def _parse_contents(self, root):
        dependencies = set()
        contents = root.get(ModelProperties.contents.value, None)

        if isinstance(contents, list):
            for item in contents:
                dependencies.update(
                    self._parse_component(item.get(ModelProperties.schema.value))
                )

        return list(dependencies)

    def _parse_component(self, component):
        dependencies = set()
        if isinstance(component, text_type) and is_valid_dtmi(component):
            dependencies.add(component)
        elif isinstance(component, list):
            # If it's a list, could have DTMIs or nested models
            for item in component:
                if isinstance(item, text_type):
                    # If there are strings in the list, that's a DTMI reference, so add it
                    dependencies.add(item)
                elif _is_interface_or_component(item):
                    # This is a nested model. Now go get its dependencies and add them
                    dependencies.update(self._parse_interface(item).dependencies)
        elif _is_interface_or_component(component):
            metadata = self._parse_interface(component).dependencies
            dependencies.update(metadata)
        return list(dependencies)

def _is_interface_or_component(root):
    if not isinstance(root, dict):
        return False

    interface = root.get(ModelProperties.type.value)
    return (
        isinstance(interface, text_type) and
        interface in [ModelType.interface.value, ModelType.component.value]
    )
