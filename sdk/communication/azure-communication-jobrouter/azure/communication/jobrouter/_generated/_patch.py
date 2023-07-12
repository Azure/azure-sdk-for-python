# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from azure.core.exceptions import DeserializationError, SerializationError, raise_with_traceback

from ._serialization import basestring, unicode_str, _FLATTEN, _decode_attribute_map_key
from ._serialization import Deserializer as DeserializerGenerated


class Deserializer(DeserializerGenerated):
    @staticmethod
    def _flatten_subtype(cls, key, objects):
        if "_subtype_map" not in cls.__dict__:
            return {}
        result = dict(cls._subtype_map[key])
        for valuetype in cls._subtype_map[key].values():
            result.update(Deserializer._flatten_subtype(objects[valuetype], key, objects))
        return result

    @staticmethod
    def _get_rest_key_parts(cls, attr_key):
        """Get the RestAPI key of this attr, split it and decode part
        :param str attr_key: Attribute key must be in attribute_map.
        :returns: A list of RestAPI part
        :rtype: list
        """
        rest_split_key = _FLATTEN.split(cls._attribute_map[attr_key]["key"])
        return [_decode_attribute_map_key(key_part) for key_part in rest_split_key]

    def _classify_target(self, target, data):
        """Overload for _classify_target to accommodate for handwritten models
        Check to see whether the deserialization target object can
        be classified into a subclass.
        Once classification has been determined, initialize object.

        :param str target: The target object type to deserialize to.
        :param str/dict data: The response data to deserialize.
        """

        if target is None:
            return None, None

        if isinstance(target, basestring):
            try:
                target = self.dependencies[target]
            except KeyError:
                return target, target

        # Target is not a Model, perform a manual search
        subtype_keys = target.__dict__.get("_subtype_map", {}).keys()
        for subtype_key in subtype_keys:
            rest_api_response_key = Deserializer._get_rest_key_parts(target, subtype_key)[-1]
            subtype_value = data.pop(rest_api_response_key, None) or data.pop(subtype_key, None)

            if subtype_value:
                if target.__name__ == subtype_value:
                    target = target
                flatten_mapping_type = Deserializer._flatten_subtype(target, subtype_key, self.dependencies)
                try:
                    target = self.dependencies[flatten_mapping_type[subtype_value]]
                except KeyError:
                    raise_with_traceback(DeserializationError, "Failed to deserialize: " + target.__class__.__name__)

        return target, target.__class__.__name__  # type: ignore


__all__: List[str] = ["Deserializer"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
