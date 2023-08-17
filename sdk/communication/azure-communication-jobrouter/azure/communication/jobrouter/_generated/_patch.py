# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from azure.core.exceptions import DeserializationError, SerializationError, raise_with_traceback

from ._serialization import (
    basestring,
    unicode_str,
    _FLATTEN,
    _decode_attribute_map_key,
    Deserializer as DeserializerGenerated,
    Serializer as SerializerGenerated,
    rest_key_case_insensitive_extractor,
    attribute_key_case_insensitive_extractor,
    last_rest_key_case_insensitive_extractor,
    Model,
    Enum,
    _LOGGER,
    AzureCoreNull
)


class Serializer(SerializerGenerated):

    def body(self, data, data_type, **kwargs):
        """Serialize data intended for a request body.

        :param data: The data to be serialized.
        :param str data_type: The type to be serialized from.
        :rtype: dict
        :raises: SerializationError if serialization fails.
        :raises: ValueError if data is None
        """
        # This is code is replicating the base class with JobRouter's custom Deserializer
        # Just in case this is a dict
        internal_data_type_str = data_type.strip("[]{}")
        internal_data_type = self.dependencies.get(internal_data_type_str, None)
        try:
            is_xml_model_serialization = kwargs["is_xml"]
        except KeyError:
            if internal_data_type and issubclass(internal_data_type, Model):
                is_xml_model_serialization = kwargs.setdefault("is_xml", internal_data_type.is_xml_model())
            else:
                is_xml_model_serialization = False
        if internal_data_type and not isinstance(internal_data_type, Enum):
            try:
                deserializer = Deserializer(self.dependencies)
                # Since it's on serialization, it's almost sure that format is not JSON REST
                # We're not able to deal with additional properties for now.
                deserializer.additional_properties_detection = False
                if is_xml_model_serialization:
                    deserializer.key_extractors = [  # type: ignore
                        attribute_key_case_insensitive_extractor,
                    ]
                else:
                    deserializer.key_extractors = [
                        rest_key_case_insensitive_extractor,
                        attribute_key_case_insensitive_extractor,
                        last_rest_key_case_insensitive_extractor,
                    ]
                data = deserializer._deserialize(data_type, data)
            except DeserializationError as err:
                raise_with_traceback(SerializationError, "Unable to build a model: " + str(err), err)

        return self._serialize(data, data_type, **kwargs)

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

    def _deserialize(self, target_obj, data):
        """Call the deserializer on a model.

        Data needs to be already deserialized as JSON or XML ElementTree

        :param str target_obj: Target data type to deserialize to.
        :param object data: Object to deserialize.
        :raises: DeserializationError if deserialization fails.
        :return: Deserialized object.

        """
        # This is code is replicating the base class with JobRouter's custom deserialization logic
        # This is already a model, go recursive just in case
        if hasattr(data, "_attribute_map"):
            constants = [name for name, config in getattr(data, "_validation", {}).items() if config.get("constant")]
            try:
                for attr, mapconfig in data._attribute_map.items():
                    if attr in constants:
                        continue
                    value = getattr(data, attr)
                    if value is None or value is AzureCoreNull:
                        continue
                    local_type = mapconfig["type"]
                    internal_data_type = local_type.strip("[]{}")
                    if internal_data_type not in self.dependencies or isinstance(internal_data_type, Enum):
                        continue
                    setattr(data, attr, self._deserialize(local_type, value))
                return data
            except AttributeError:
                return

        response, class_name = self._classify_target(target_obj, data)

        if isinstance(response, basestring):
            return self.deserialize_data(data, response)
        elif isinstance(response, type) and issubclass(response, Enum):
            return self.deserialize_enum(data, response)

        if data is None:
            return data
        try:
            attributes = response._attribute_map  # type: ignore
            d_attrs = {}
            for attr, attr_desc in attributes.items():
                # Check empty string. If it's not empty, someone has a real "additionalProperties"...
                if attr == "additional_properties" and attr_desc["key"] == "":
                    continue
                raw_value = None
                # Enhance attr_desc with some dynamic data
                attr_desc = attr_desc.copy()  # Do a copy, do not change the real one
                internal_data_type = attr_desc["type"].strip("[]{}")
                if internal_data_type in self.dependencies:
                    attr_desc["internalType"] = self.dependencies[internal_data_type]

                for key_extractor in self.key_extractors:
                    found_value = key_extractor(attr, attr_desc, data)
                    if found_value is not None:
                        if raw_value is not None and raw_value != found_value:
                            msg = (
                                "Ignoring extracted value '%s' from %s for key '%s'"
                                " (duplicate extraction, follow extractors order)"
                            )
                            _LOGGER.warning(msg, found_value, key_extractor, attr)
                            continue
                        raw_value = found_value

                value = self.deserialize_data(raw_value, attr_desc["type"])
                d_attrs[attr] = value
        except (AttributeError, TypeError, KeyError) as err:
            msg = "Unable to deserialize to object: " + class_name  # type: ignore
            raise_with_traceback(DeserializationError, msg, err)
        else:
            additional_properties = self._build_additional_properties(attributes, data)
            return self._instantiate_model(response, d_attrs, additional_properties)

__all__: List[str] = ["Deserializer", "Serializer"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
