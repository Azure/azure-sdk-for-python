# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""The modelerfour reformatter autorest plugin.
"""
import re
import copy
import logging
from typing import Callable, Dict, Any, Iterable, List, Optional, Set

from .._utils import (
    to_snake_case,
    KNOWN_TYPES,
    get_body_type_for_description,
    JSON_REGEXP,
)
from .. import YamlUpdatePluginAutorest


ORIGINAL_ID_TO_UPDATED_TYPE: Dict[int, Dict[str, Any]] = {}
OAUTH_TYPE = "OAuth2"
KEY_TYPE = "Key"

_LOGGER = logging.getLogger(__name__)


def is_body(yaml_data: Dict[str, Any]) -> bool:
    """Return true if passed in parameter is a body param"""
    return yaml_data["protocol"]["http"]["in"] == "body"


def get_body_parameter(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a request's body parameter"""
    return next(p for p in yaml_data["parameters"] if is_body(p))


def get_azure_key_credential(key: str) -> Dict[str, Any]:
    retval = {
        "type": KEY_TYPE,
        "policy": {"type": "AzureKeyCredentialPolicy", "key": key},
    }
    update_type(retval)
    return retval


def get_type(yaml_data: Dict[str, Any]):
    try:
        return ORIGINAL_ID_TO_UPDATED_TYPE[id(yaml_data)]
    except KeyError:
        return KNOWN_TYPES[yaml_data["type"]]


def _get_api_versions(api_versions: List[Dict[str, str]]) -> List[str]:
    return list({api_version["version"]: None for api_version in api_versions}.keys())


def _update_type_base(updated_type: str, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": updated_type,
        "clientDefaultValue": yaml_data.get("defaultValue"),
        "xmlMetadata": yaml_data.get("serialization", {}).get("xml", {}),
        "apiVersions": _get_api_versions(yaml_data.get("apiVersions", [])),
    }


def update_list(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    base = _update_type_base("list", yaml_data)
    base["elementType"] = update_type(yaml_data["elementType"])
    base["maxItems"] = yaml_data.get("maxItems")
    base["minItems"] = yaml_data.get("minItems")
    base["uniqueItems"] = yaml_data.get("uniqueItems", False)
    return base


def update_dict(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    base = _update_type_base("dict", yaml_data)
    base["elementType"] = update_type(yaml_data["elementType"])
    return base


def update_constant(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    base = _update_type_base("constant", yaml_data)
    base["valueType"] = update_type(yaml_data["valueType"])
    base["value"] = yaml_data["value"]["value"]
    return base


def update_enum_value(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": yaml_data["language"]["default"]["name"],
        "value": yaml_data["value"],
        "description": yaml_data["language"]["default"]["description"],
    }


def update_enum(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    base = _update_type_base("enum", yaml_data)
    base.update(
        {
            "name": yaml_data["language"]["default"]["name"],
            "valueType": update_type(yaml_data["choiceType"]),
            "values": [update_enum_value(v) for v in yaml_data["choices"]],
            "description": yaml_data["language"]["default"]["description"],
        }
    )
    return base


def update_property(
    yaml_data: Dict[str, Any], has_additional_properties: bool
) -> Dict[str, Any]:
    client_name = yaml_data["language"]["default"]["name"]
    if has_additional_properties and client_name == "additional_properties":
        client_name = "additional_properties1"
    return {
        "clientName": client_name,
        "wireName": yaml_data["serializedName"],
        "flattenedNames": yaml_data.get("flattenedNames", []),
        "type": update_type(yaml_data["schema"]),
        "optional": not yaml_data.get("required"),
        "description": yaml_data["language"]["default"]["description"],
        "isDiscriminator": yaml_data.get("isDiscriminator"),
        "readonly": yaml_data.get("readOnly", False),
        "groupedParameterNames": [
            op["language"]["default"]["name"].lstrip("_")  # TODO: patching m4
            for op in yaml_data.get("originalParameter", [])
        ],
        "clientDefaultValue": yaml_data.get("clientDefaultValue"),
    }


def update_discriminated_subtypes(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        obj["discriminatorValue"]: update_type(obj)
        for obj in yaml_data.get("discriminator", {}).get("immediate", {}).values()
    }


def create_model(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    base = _update_type_base("model", yaml_data)
    base["name"] = yaml_data["language"]["default"]["name"]
    base["description"] = yaml_data["language"]["default"]["description"]
    base["isXml"] = "xml" in yaml_data.get("serializationFormats", [])
    base["base"] = "msrest"
    return base


def fill_model(
    yaml_data: Dict[str, Any], current_model: Dict[str, Any]
) -> Dict[str, Any]:
    properties = []
    yaml_parents = yaml_data.get("parents", {}).get("immediate", [])
    dict_parents = [p for p in yaml_parents if p["type"] == "dictionary"]
    if dict_parents:
        # add additional properties property
        properties.append(
            {
                "clientName": "additional_properties",
                "wireName": "",
                "type": update_type(dict_parents[0]),
                "optional": True,
                "description": "Unmatched properties from the message are deserialized to this collection.",
                "isDiscriminator": False,
                "readonly": False,
            }
        )
    properties.extend(
        [
            update_property(p, has_additional_properties=bool(dict_parents))
            for p in yaml_data.get("properties", [])
        ]
    )
    current_model.update(
        {
            "properties": properties,
            "parents": [
                update_type(yaml_data=p) for p in yaml_parents if p["type"] == "object"
            ],
            "discriminatedSubtypes": update_discriminated_subtypes(yaml_data),
            "discriminatorValue": yaml_data.get("discriminatorValue"),
        }
    )
    return current_model


def update_number_type(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    updated_type = "integer" if yaml_data["type"] == "integer" else "float"
    base = _update_type_base(updated_type, yaml_data)
    base.update(
        {
            "precision": yaml_data.get("precision"),
            "multipleOf": yaml_data.get("multipleOf"),
            "maximum": yaml_data.get("maximum"),
            "minimum": yaml_data.get("minimum"),
            "exclusiveMaximum": yaml_data.get("exclusiveMaximum"),
            "exclusiveMinimum": yaml_data.get("exclusiveMinimum"),
        }
    )
    return base


def update_primitive(  # pylint: disable=too-many-return-statements
    type_group: str, yaml_data: Dict[str, Any]
) -> Dict[str, Any]:
    if type_group in ("integer", "number"):
        return update_number_type(yaml_data)
    if type_group in ("string", "uuid", "uri"):
        if any(
            r in yaml_data
            for r in (
                "maxLength",
                "minLength",
                "pattern",
                "defaultValue",
                "serialization",
            )
        ):
            base = _update_type_base("string", yaml_data)
            base.update(
                {
                    "maxLength": yaml_data.get("maxLength"),
                    "minLength": yaml_data.get("minLength"),
                    "pattern": yaml_data.get("pattern"),
                }
            )
            return base
        return KNOWN_TYPES["string"]
    if type_group == "binary":
        return KNOWN_TYPES["binary"]
    if type_group == "date-time":
        base = _update_type_base("datetime", yaml_data)
        base["format"] = yaml_data["format"]
        return base
    if type_group == "byte-array":
        base = _update_type_base("bytes", yaml_data)
        base["format"] = yaml_data["format"]
        return base
    return _update_type_base(type_group, yaml_data)


def update_types(yaml_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    types: List[Dict[str, Any]] = []
    for type in yaml_data:
        if KNOWN_TYPES.get(type["type"]):
            types.append(KNOWN_TYPES[type["type"]])
        else:
            types.append(
                next(
                    v for v in ORIGINAL_ID_TO_UPDATED_TYPE.values() if id(v) == id(type)
                )
            )
    retval = {"type": "combined", "types": types}
    ORIGINAL_ID_TO_UPDATED_TYPE[id(retval)] = retval
    return retval


def update_type(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    if id(yaml_data) in ORIGINAL_ID_TO_UPDATED_TYPE:
        return ORIGINAL_ID_TO_UPDATED_TYPE[id(yaml_data)]
    type_group = yaml_data["type"]
    if type_group == "array":
        updated_type = update_list(yaml_data)
    elif type_group == "dictionary":
        updated_type = update_dict(yaml_data)
    elif type_group == "constant":
        updated_type = update_constant(yaml_data)
    elif type_group in ("choice", "sealed-choice"):
        updated_type = update_enum(yaml_data)
    elif type_group in (OAUTH_TYPE, KEY_TYPE):
        updated_type = yaml_data
    elif type_group in ("object", "group"):
        # avoiding infinite loop
        initial_model = create_model(yaml_data)
        ORIGINAL_ID_TO_UPDATED_TYPE[id(yaml_data)] = initial_model
        updated_type = fill_model(yaml_data, initial_model)
    else:
        updated_type = update_primitive(type_group, yaml_data)
    ORIGINAL_ID_TO_UPDATED_TYPE[id(yaml_data)] = updated_type
    return updated_type


def update_parameter_delimiter(style: Optional[str]) -> Optional[str]:
    if not style:
        return None
    if style in ("form", "simple"):
        return "comma"
    if style in ("spaceDelimited", "pipeDelimited", "tabDelimited"):
        return style.replace("Delimited", "")
    return None


def get_all_body_types(yaml_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    seen_body_types = {}
    for schema_request in yaml_data.values():
        body_param = get_body_parameter(schema_request)
        seen_body_types[id(body_param["schema"])] = update_type(body_param["schema"])
    return list(seen_body_types.values())


def add_lro_information(
    operation: Dict[str, Any],
    initial_operation: Dict[str, Any],
    yaml_data: Dict[str, Any],
) -> None:
    operation["discriminator"] = "lro"
    extensions = yaml_data["extensions"]
    operation["lroOptions"] = extensions.get("x-ms-long-running-operation-options")
    operation["initialOperation"] = initial_operation
    for response in operation["responses"]:
        response["pollerSync"] = extensions.get("x-python-custom-poller-sync")
        response["pollerAsync"] = extensions.get("x-python-custom-poller-async")
        response["pollingMethodSync"] = extensions.get(
            "x-python-custom-default-polling-method-sync"
        )
        response["pollingMethodAsync"] = extensions.get(
            "x-python-custom-default-polling-method-async"
        )


def filter_out_paging_next_operation(
    yaml_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    next_operations: Set[str] = set()
    for operation in yaml_data:
        next_operation = operation.get("nextOperation")
        if not next_operation:
            continue
        next_operations.add(next_operation["name"])
    return [o for o in yaml_data if o["name"] not in next_operations]


def update_response_header(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "wireName": yaml_data["header"],
        "type": update_type(yaml_data["schema"]),
    }


def update_response(
    yaml_data: Dict[str, Any],
) -> Dict[str, Any]:
    if yaml_data.get("binary"):
        type = KNOWN_TYPES["binary"]
    elif yaml_data.get("schema"):
        type = get_type(yaml_data["schema"])
    else:
        type = None
    return {
        "headers": [
            update_response_header(h)
            for h in yaml_data["protocol"]["http"].get("headers", [])
        ],
        "statusCodes": [
            int(code) if code != "default" else "default"
            for code in yaml_data["protocol"]["http"]["statusCodes"]
        ],
        "type": type,
        "nullable": yaml_data.get("nullable", False),
    }


def _get_default_content_type(  # pylint: disable=too-many-return-statements
    content_types: Iterable[str],
) -> Optional[str]:
    json_values = [ct for ct in content_types if JSON_REGEXP.match(ct.split(";")[0])]
    if json_values:
        if "application/json" in json_values:
            return "application/json"
        return json_values[0]

    xml_values = [ct for ct in content_types if "xml" in ct]
    if xml_values:
        if "application/xml" in xml_values:
            return "application/xml"
        return xml_values[0]

    if "application/octet-stream" in content_types:
        return "application/octet-stream"
    if "application/x-www-form-urlencoded" in content_types:
        return "application/x-www-form-urlencoded"
    return None


def update_client_url(yaml_data: Dict[str, Any]) -> str:
    if any(
        p
        for p in yaml_data["globalParameters"]
        if p["language"]["default"]["name"] == "$host"
    ):
        # this means we DO NOT have a parameterized host
        # in order to share code better, going to make it a "parameterized host" of
        # just the endpoint parameter
        return "{endpoint}"
    # we have a parameterized host. Return first url from first request, quite gross
    return yaml_data["operationGroups"][0]["operations"][0]["requests"][0]["protocol"][
        "http"
    ]["uri"]


def to_lower_camel_case(name: str) -> str:
    return re.sub(r"_([a-z])", lambda x: x.group(1).upper(), name)


class M4Reformatter(
    YamlUpdatePluginAutorest
):  # pylint: disable=too-many-public-methods
    """Add Python naming information."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.check_client_input: bool = False

    @property
    def azure_arm(self) -> bool:
        return bool(self._autorestapi.get_boolean_value("azure-arm"))

    @property
    def version_tolerant(self) -> bool:
        return bool(self._autorestapi.get_boolean_value("version-tolerant"))

    @property
    def low_level_client(self) -> bool:
        return bool(self._autorestapi.get_boolean_value("low-level-client"))

    @property
    def legacy(self) -> bool:
        return not (self.version_tolerant or self.low_level_client)

    @property
    def only_path_and_body_parameters_positional(self) -> bool:
        return self.version_tolerant or bool(
            self._autorestapi.get_boolean_value("only-path-and-body-params-positional")
        )

    @property
    def default_optional_constants_to_none(self) -> bool:
        return bool(
            self._autorestapi.get_boolean_value("default-optional-constants-to-none")
            or self.version_tolerant
        )

    def update_parameter_base(
        self, yaml_data: Dict[str, Any], *, override_client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        location = yaml_data["protocol"].get("http", {}).get("in")
        if not location:
            location = "other"
        if location == "uri":
            location = "endpointPath"
        grouped_by = (
            yaml_data["groupedBy"]["language"]["default"]["name"]
            if yaml_data.get("groupedBy")
            else None
        )
        client_name: str = (
            override_client_name or yaml_data["language"]["default"]["name"]
        )
        if grouped_by and client_name[0] != "_":
            # this is an m4 bug, doesn't hide constant grouped params, patching m4 for now
            client_name = "_" + client_name
        if yaml_data.get("origin") == "modelerfour:synthesized/api-version":
            yaml_data["inDocstring"] = False
            if self.legacy:
                yaml_data["implementation"] = "Method"
                yaml_data["checkClientInput"] = self.check_client_input
            yaml_data["isApiVersion"] = True
        return {
            "optional": not yaml_data.get("required", False),
            "description": yaml_data["language"]["default"]["description"],
            "clientName": client_name,
            "wireName": yaml_data["language"]["default"].get("serializedName"),
            "clientDefaultValue": yaml_data.get("clientDefaultValue"),
            "location": location,
            "groupedBy": grouped_by,
            "checkClientInput": yaml_data.get("checkClientInput", False),
            "inDocstring": yaml_data.get("inDocstring", True),
            "isApiVersion": yaml_data.get("isApiVersion", False),
            "implementation": yaml_data.get("implementation"),
        }

    def update_overloads(
        self,
        group_name: str,
        yaml_data: Dict[str, Any],
        body_parameter: Optional[Dict[str, Any]],
        *,
        content_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        overloads: List[Dict[str, Any]] = []
        if not body_parameter:
            return overloads
        body_types = body_parameter["type"].get("types", [])
        if not body_types:
            return overloads
        for body_type in body_types:
            overload = self.update_overload(
                group_name, yaml_data, body_type, content_types=content_types
            )
            overload["internal"] = yaml_data.get("extensions", {}).get(
                "x-ms-internal", False
            )
            for parameter in overload["parameters"]:
                if parameter["wireName"].lower() == "content-type":
                    parameter["clientDefaultValue"] = overload["bodyParameter"][
                        "defaultContentType"
                    ]
            overloads.append(overload)
        return overloads

    def _update_operation_helper(
        self,
        group_name: str,
        yaml_data: Dict[str, Any],
        body_parameter: Optional[Dict[str, Any]],
        *,
        is_overload: bool = False,
    ) -> Dict[str, Any]:
        in_overriden = (
            body_parameter["type"]["type"] == "combined" if body_parameter else False
        )
        abstract = False
        if body_parameter and (
            body_parameter.get("entries")
            or len(body_parameter["type"].get("types", [])) > 2
        ):
            # this means it's formdata or urlencoded, or there are more than 2 types of body
            abstract = True
        return {
            "name": yaml_data["language"]["default"]["name"],
            "description": yaml_data["language"]["default"]["description"],
            "summary": yaml_data["language"]["default"].get("summary"),
            "url": yaml_data["requests"][0]["protocol"]["http"]["path"],
            "method": yaml_data["requests"][0]["protocol"]["http"]["method"].upper(),
            "parameters": self.update_parameters(
                yaml_data,
                body_parameter,
                in_overload=is_overload,
                in_overriden=in_overriden,
            ),
            "bodyParameter": body_parameter,
            "responses": [update_response(r) for r in yaml_data.get("responses", [])],
            "exceptions": [
                update_response(e)
                for e in yaml_data.get("exceptions", [])
                if not (
                    e.get("schema")
                    and e["schema"]["language"]["default"]["name"] == "CloudError"
                )
            ],
            "groupName": group_name,
            "discriminator": "operation",
            "isOverload": is_overload,
            "apiVersions": _get_api_versions(yaml_data.get("apiVersions", [])),
            "abstract": abstract,
            "externalDocs": yaml_data.get("externalDocs"),
        }

    def get_operation_creator(
        self, yaml_data: Dict[str, Any]
    ) -> Callable[[str, Dict[str, Any]], List[Dict[str, Any]]]:
        lro_operation = yaml_data.get("extensions", {}).get(
            "x-ms-long-running-operation"
        )
        paging_operation = yaml_data.get("extensions", {}).get("x-ms-pageable")
        if lro_operation and paging_operation:
            return self.update_lro_paging_operation
        if lro_operation:
            return self.update_lro_operation
        if paging_operation:
            return self.update_paging_operation
        return self.update_operation

    def update_operation(
        self, group_name: str, yaml_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        body_parameter = (
            self.update_body_parameter(yaml_data["requestMediaTypes"])
            if yaml_data.get("requestMediaTypes")
            else None
        )
        content_types = None
        operation = self._update_operation_helper(group_name, yaml_data, body_parameter)
        operation["internal"] = yaml_data.get("extensions", {}).get(
            "x-ms-internal", False
        )
        operation["overloads"] = self.update_overloads(
            group_name, yaml_data, body_parameter, content_types=content_types
        )
        operation["samples"] = yaml_data.get("extensions", {}).get("x-ms-examples", {})
        return [operation]

    def add_paging_information(
        self, group_name: str, operation: Dict[str, Any], yaml_data: Dict[str, Any]
    ) -> None:
        operation["discriminator"] = "paging"
        operation["itemName"] = yaml_data["extensions"]["x-ms-pageable"].get(
            "itemName", "value"
        )
        operation["continuationTokenName"] = yaml_data["extensions"][
            "x-ms-pageable"
        ].get("nextLinkName")
        returned_response_object = (
            operation["nextOperation"]["responses"][0]
            if operation.get("nextOperation")
            else operation["responses"][0]
        )
        if self.version_tolerant:
            # if we're in version tolerant, hide the paging model
            returned_response_object["type"]["internal"] = True
        operation["itemType"] = next(
            p["type"]
            for p in returned_response_object["type"]["properties"]
            if p["wireName"] == operation["itemName"]
        )
        if yaml_data["language"]["default"]["paging"].get("nextLinkOperation"):
            operation["nextOperation"] = self.update_operation(
                group_name=group_name,
                yaml_data=yaml_data["language"]["default"]["paging"][
                    "nextLinkOperation"
                ],
            )[0]
        extensions = yaml_data["extensions"]
        for response in operation["responses"]:
            response["pagerSync"] = extensions.get("x-python-custom-pager-sync")
            response["pagerAsync"] = extensions.get("x-python-custom-pager-async")

    def update_paging_operation(
        self, group_name: str, yaml_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        retval: List[Dict[str, Any]] = []
        for base_operation in self.update_operation(group_name, yaml_data):
            self.add_paging_information(group_name, base_operation, yaml_data)
            retval.append(base_operation)
        return retval

    def update_lro_paging_operation(
        self, group_name: str, yaml_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        retval: List[Dict[str, Any]] = []
        for operation in self.update_lro_operation(group_name, yaml_data):
            if operation.get("discriminator") == "lro":
                self.add_paging_information(group_name, operation, yaml_data)
                operation["discriminator"] = "lropaging"
            retval.append(operation)
        return retval

    def update_lro_initial_operation(self, initial_operation: Dict[str, Any]):
        initial_operation["name"] = f"_{initial_operation['name']}_initial"
        initial_operation["isLroInitialOperation"] = True
        initial_operation["wantTracing"] = False
        return initial_operation

    def update_lro_operation(
        self, group_name: str, yaml_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        retval: List[Dict[str, Any]] = []
        for base_operation in self.update_operation(group_name, yaml_data):
            initial_operation = self.update_operation(group_name, yaml_data)[0]
            self.update_lro_initial_operation(initial_operation)
            add_lro_information(base_operation, initial_operation, yaml_data)
            for overload in base_operation["overloads"]:
                add_lro_information(overload, initial_operation, yaml_data)
            retval.append(initial_operation)
            retval.append(base_operation)
        return retval

    def update_overload(
        self,
        group_name: str,
        yaml_data: Dict[str, Any],
        body_type: Dict[str, Any],
        *,
        content_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        body_parameter = self.update_body_parameter_overload(
            yaml_data["requestMediaTypes"], body_type, content_types=content_types
        )
        return self._update_operation_helper(
            group_name, yaml_data, body_parameter, is_overload=True
        )

    def update_operation_group(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        property_name = yaml_data["language"]["default"]["name"]
        return {
            "propertyName": property_name,
            "className": property_name,
            "operations": filter_out_paging_next_operation(
                [
                    o
                    for ydo in yaml_data["operations"]
                    for o in self.get_operation_creator(ydo)(property_name, ydo)
                ]
            ),
        }

    def _update_body_parameter_helper(
        self,
        yaml_data: Dict[str, Any],
        body_param: Dict[str, Any],
        body_type: Dict[str, Any],
        *,
        content_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        flattened = body_param.get("flattened")
        is_partial_body = body_param.get("isPartialBody")
        param_base = self.update_parameter_base(body_param)
        body_param = copy.deepcopy(param_base)
        body_param["type"] = body_type
        body_param["contentTypes"] = content_types or [
            ct
            for ct, request in yaml_data.items()
            if id(body_type)
            == id(
                ORIGINAL_ID_TO_UPDATED_TYPE[id(get_body_parameter(request)["schema"])]
            )
        ]
        # get default content type
        body_param["defaultContentType"] = _get_default_content_type(
            body_param["contentTypes"]
        )
        # python supports IO input with all kinds of content_types
        if body_type["type"] == "binary":
            body_param["contentTypes"] = content_types or list(yaml_data.keys())
        if body_param["type"]["type"] == "constant":
            if not body_param["optional"] or (
                body_param["optional"] and not self.default_optional_constants_to_none
            ):
                body_param["clientDefaultValue"] = body_type["value"]
        body_param["flattened"] = flattened
        body_param["isPartialBody"] = is_partial_body
        body_param["wireName"] = body_param["wireName"] or to_lower_camel_case(
            body_param["clientName"]
        )
        return body_param

    def update_multipart_body_parameter(
        self, yaml_data: Dict[str, Any], client_name: str, description: str
    ) -> Dict[str, Any]:
        first_value = list(yaml_data.values())[0]
        entries = [
            self._update_body_parameter_helper(yaml_data, p, update_type(p["schema"]))
            for p in first_value["parameters"]
            if is_body(p)
        ]
        return {
            "optional": not first_value.get("required", False),
            "description": description,
            "clientName": client_name,
            "wireName": client_name,
            "clientDefaultValue": None,
            "location": "Method",
            "type": KNOWN_TYPES["anydict"],
            "contentTypes": list(yaml_data.keys()),
            "defaultContentType": _get_default_content_type(yaml_data.keys()),
            "entries": entries,
        }

    def update_body_parameter(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        protocol_http = list(yaml_data.values())[0].get("protocol", {}).get("http", {})
        if protocol_http.get("multipart"):
            return self.update_multipart_body_parameter(
                yaml_data, "files", "Multipart input for files."
            )
        if protocol_http.get("knownMediaType") == "form":
            return self.update_multipart_body_parameter(
                yaml_data, "data", "Multipart input for form encoded data."
            )
        body_types = get_all_body_types(yaml_data)
        if len(body_types) > 1 and not yaml_data.get("flattened"):
            body_type = update_types(body_types)
        else:
            body_type = body_types[0]
        body_param = next(
            p for sr in yaml_data.values() for p in sr["parameters"] if is_body(p)
        )
        return self._update_body_parameter_helper(yaml_data, body_param, body_type)

    def update_body_parameter_overload(
        self,
        yaml_data: Dict[str, Any],
        body_type: Dict[str, Any],
        *,
        content_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """For overloads we already know what body_type we want to go with"""
        body_param = next(
            p for sr in yaml_data.values() for p in sr["parameters"] if is_body(p)
        )
        return self._update_body_parameter_helper(
            yaml_data, body_param, body_type, content_types=content_types
        )

    def update_flattened_parameter(
        self, yaml_data: Dict[str, Any], body_parameter: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not body_parameter:
            raise ValueError("Has to have a body parameter if it's flattened")
        # this means i'm a property that is part of a flattened model
        target_property_name = yaml_data["targetProperty"]["language"]["default"][
            "name"
        ]
        param = self.update_parameter(yaml_data)
        body_parameter.setdefault("propertyToParameterName", {})[
            target_property_name
        ] = param["clientName"]
        param["inFlattenedBody"] = True
        return param

    def _update_content_type_parameter(
        self,
        yaml_data: Dict[str, Any],
        body_parameter: Optional[Dict[str, Any]],
        request_media_types: List[str],
        *,
        in_overload: bool = False,
        in_overriden: bool = False,
    ) -> Dict[str, Any]:
        # override content type type to string
        if not body_parameter:
            return yaml_data
        param = copy.deepcopy(yaml_data)
        param["schema"] = KNOWN_TYPES["string"]  # override to string type
        if (
            body_parameter["type"]["type"] == "binary"
            and not body_parameter["defaultContentType"]
            and not self.legacy
        ):
            param["required"] = True
        else:
            param["required"] = False
        description = param["language"]["default"]["description"]
        if description and description[-1] != ".":
            description += "."
        if not (in_overriden or in_overload):
            param["inDocstring"] = False
        elif in_overload:
            description += (
                " Content type parameter for "
                f"{get_body_type_for_description(body_parameter)} body."
            )
        if not in_overload or (
            body_parameter["type"]["type"] == "binary" and len(request_media_types) > 1
        ):
            content_types = "'" + "', '".join(request_media_types) + "'"
            description += f" Known values are: {content_types}."
        if not in_overload and not in_overriden:
            param["clientDefaultValue"] = body_parameter["defaultContentType"]
        param["language"]["default"]["description"] = description
        return param

    def _update_parameters_helper(
        self,
        parameters: List[Dict[str, Any]],
        body_parameter: Optional[Dict[str, Any]],
        seen_client_names: Set[str],
        groupers: Dict[str, Dict[str, Any]],
        request_media_types: List[str],
        *,
        in_overload: bool = False,
        in_overriden: bool = False,
    ) -> List[Dict[str, Any]]:
        retval: List[Dict[str, Any]] = []
        has_flattened_body = body_parameter and body_parameter.get("flattened")
        for param in parameters:
            client_name = param["language"]["default"]["name"]
            if param["language"]["default"]["name"] == "$host" or (
                client_name in seen_client_names
            ):
                continue
            seen_client_names.add(client_name)
            if has_flattened_body and param.get("targetProperty"):
                retval.append(self.update_flattened_parameter(param, body_parameter))
                continue
            if param["schema"]["type"] == "group":
                # this means i'm a parameter group parameter
                param = self.update_parameter(param)
                param["grouper"] = True
                groupers[param["clientName"]] = param
                retval.append(param)
                continue
            if is_body(param):
                continue
            if (
                param["language"]["default"].get("serializedName").lower()
                == "content-type"
            ):
                param = self._update_content_type_parameter(
                    param,
                    body_parameter,
                    request_media_types,
                    in_overload=in_overload,
                    in_overriden=in_overriden,
                )
            updated_param = self.update_parameter(
                param, in_overload=in_overload, in_overriden=in_overriden
            )
            retval.append(updated_param)
        return retval

    def update_parameters(
        self,
        yaml_data: Dict[str, Any],
        body_parameter: Optional[Dict[str, Any]],
        *,
        in_overload: bool = False,
        in_overriden: bool = False,
    ) -> List[Dict[str, Any]]:
        retval: List[Dict[str, Any]] = []
        seen_client_names: Set[str] = set()
        groupers: Dict[str, Dict[str, Any]] = {}
        # first update top level parameters
        request_media_types = yaml_data.get("requestMediaTypes", [])
        retval.extend(
            self._update_parameters_helper(
                yaml_data["parameters"],
                body_parameter,
                seen_client_names,
                groupers,
                request_media_types,
                in_overload=in_overload,
                in_overriden=in_overriden,
            )
        )
        # now we handle content type and accept headers.
        # We only care about the content types on the body parameter itself,
        # so ignoring the different content types for now
        if yaml_data.get("requestMediaTypes"):
            sub_requests = yaml_data["requestMediaTypes"].values()
        else:
            sub_requests = yaml_data.get("requests", [])
        for request in sub_requests:  # pylint: disable=too-many-nested-blocks
            retval.extend(
                self._update_parameters_helper(
                    request.get("parameters", []),
                    body_parameter,
                    seen_client_names,
                    groupers,
                    request_media_types,
                    in_overload=in_overload,
                    in_overriden=in_overriden,
                )
            )
        all_params = (retval + [body_parameter]) if body_parameter else retval
        for grouper_name, grouper in groupers.items():
            grouper["propertyToParameterName"] = {
                next(
                    prop
                    for prop in grouper["type"]["properties"]
                    if p["clientName"].lstrip("_")
                    in prop["groupedParameterNames"]  # TODO: patching m4
                )["clientName"]: p["clientName"]
                for p in all_params
                if p.get("groupedBy") == grouper_name
            }
        return retval

    def update_parameter(
        self,
        yaml_data: Dict[str, Any],
        *,
        override_client_name: Optional[str] = None,
        in_overload: bool = False,
        in_overriden: bool = False,
    ) -> Dict[str, Any]:
        param_base = self.update_parameter_base(
            yaml_data, override_client_name=override_client_name
        )
        type = get_type(yaml_data["schema"])
        if type["type"] == "constant":
            if not param_base["optional"] or (
                param_base["optional"] and not self.default_optional_constants_to_none
            ):
                param_base["clientDefaultValue"] = type["value"]
        protocol_http = yaml_data["protocol"].get("http", {})
        param_base.update(
            {
                "type": type,
                "implementation": yaml_data["implementation"],
                "explode": protocol_http.get("explode", False),
                "inOverload": in_overload,
                "skipUrlEncoding": yaml_data.get("extensions", {}).get(
                    "x-ms-skip-url-encoding", False
                ),
                "inDocstring": yaml_data.get("inDocstring", True),
                "inOverriden": in_overriden,
                "delimiter": update_parameter_delimiter(protocol_http.get("style")),
            }
        )
        return param_base

    def update_global_parameters(
        self, yaml_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        global_params: List[Dict[str, Any]] = []
        for global_parameter in yaml_data:
            client_name: Optional[str] = None
            name = global_parameter["language"]["default"]["name"]
            if name == "$host":
                # I am the non-parameterized endpoint. Modify name based off of flag

                client_name = "endpoint" if self.version_tolerant else "base_url"
                global_parameter["language"]["default"]["description"] = "Service URL."
            elif (
                global_parameter.get("origin") == "modelerfour:synthesized/api-version"
            ):
                self.check_client_input = True
            param = self.update_parameter(
                global_parameter, override_client_name=client_name
            )
            if global_parameter.get("origin") == "modelerfour:synthesized/api-version":
                param["implementation"] = "Client"
                param["checkClientInput"] = False
            global_params.append(param)
        return global_params

    def get_token_credential(self, credential_scopes: List[str]) -> Dict[str, Any]:
        retval = {
            "type": OAUTH_TYPE,
            "policy": {
                "type": "BearerTokenCredentialPolicy",
                "credentialScopes": credential_scopes,
            },
        }
        update_type(retval)
        return retval

    def update_credential_from_security(
        self, yaml_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        retval: Dict[str, Any] = {}
        for scheme in yaml_data.get("schemes", []):
            if scheme["type"] == OAUTH_TYPE:
                # TokenCredential
                retval = self.get_token_credential(scheme["scopes"])
            elif scheme["type"] == KEY_TYPE:
                retval = get_azure_key_credential(scheme["name"])
        return retval

    def get_credential_scopes_from_flags(self, auth_policy: str) -> List[str]:
        if self.azure_arm:
            return ["https://management.azure.com/.default"]
        credential_scopes_temp = self._autorestapi.get_value("credential-scopes")
        credential_scopes = (
            credential_scopes_temp.split(",") if credential_scopes_temp else None
        )
        if (
            self._autorestapi.get_boolean_value("credential-scopes", False)
            and not credential_scopes
        ):
            raise ValueError(
                "--credential-scopes takes a list of scopes in comma separated format. "
                "For example: --credential-scopes=https://cognitiveservices.azure.com/.default"
            )
        if not credential_scopes:
            _LOGGER.warning(
                "You have default credential policy %s "
                "but not the --credential-scopes flag set while generating non-management plane code. "
                "This is not recommend because it forces the customer to pass credential scopes "
                "through kwargs if they want to authenticate.",
                auth_policy,
            )
            credential_scopes = []
        return credential_scopes

    def update_credential_from_flags(self) -> Dict[str, Any]:
        default_auth_policy = "BearerTokenCredentialPolicy"
        auth_policy = (
            self._autorestapi.get_value("credential-default-policy-type")
            or default_auth_policy
        )
        credential_scopes = self.get_credential_scopes_from_flags(auth_policy)
        key = self._autorestapi.get_value("credential-key-header-name")
        if auth_policy.lower() in (
            "armchallengeauthenticationpolicy",
            "bearertokencredentialpolicy",
        ):
            if key:
                raise ValueError(
                    "You have passed in a credential key header name with default credential policy type "
                    f"{auth_policy}. This is not allowed, since credential key header "
                    "name is tied with AzureKeyCredentialPolicy. Instead, with this policy it is recommend you "
                    "pass in --credential-scopes."
                )
            return self.get_token_credential(credential_scopes)
        # Otherwise you have AzureKeyCredentialPolicy
        if self._autorestapi.get_value("credential-scopes"):
            raise ValueError(
                "You have passed in credential scopes with default credential policy type "
                "AzureKeyCredentialPolicy. This is not allowed, since credential scopes is tied with "
                f"{default_auth_policy}. Instead, with this policy "
                "you must pass in --credential-key-header-name."
            )
        if not key:
            key = "api-key"
            _LOGGER.info(
                "Defaulting the AzureKeyCredentialPolicy header's name to 'api-key'"
            )
        return get_azure_key_credential(key)

    def update_credential(
        self, yaml_data: Dict[str, Any], parameters: List[Dict[str, Any]]
    ) -> None:
        # then override with credential flags
        credential_flag = (
            self._autorestapi.get_boolean_value("add-credentials", False)
            or self._autorestapi.get_boolean_value("add-credential", False)
            or self.azure_arm
        )
        if credential_flag:
            credential_type = self.update_credential_from_flags()
        else:
            credential_type = self.update_credential_from_security(yaml_data)
        if not credential_type:
            return
        credential = {
            "type": credential_type,
            "optional": False,
            "description": "Credential needed for the client to connect to Azure.",
            "clientName": "credential",
            "location": "other",
            "wireName": "credential",
            "implementation": "Client",
            "skipUrlEncoding": True,
            "inOverload": False,
        }
        if self.version_tolerant:
            parameters.append(credential)
        else:
            parameters.insert(0, credential)

    def update_client(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        parameters = self.update_global_parameters(
            yaml_data.get("globalParameters", [])
        )
        self.update_credential(yaml_data.get("security", {}), parameters)
        return {
            "name": yaml_data["language"]["default"]["name"],
            "description": yaml_data["info"].get("description"),
            "parameters": parameters,
            "url": update_client_url(yaml_data)
            if yaml_data.get("globalParameters")
            else "",
        }

    def update_yaml(self, yaml_data: Dict[str, Any]) -> None:
        """Convert in place the YAML str."""
        # there can only be one namespace and client from swagger
        namespace = self._autorestapi.get_value("namespace") or to_snake_case(
            yaml_data["info"]["title"].replace(" ", "")
        )
        # First we update the types, so we can access for when we're creating parameters etc.
        for type_group, types in yaml_data["schemas"].items():
            for t in types:
                if (
                    type_group == "objects"
                    and t["language"]["default"]["name"] == "CloudError"
                ):
                    # we don't generate cloud error
                    continue
                update_type(t)
        yaml_data["namespace"] = namespace
        yaml_data["subnamespaceToClients"] = {}
        yaml_data["clients"] = [self.update_client(yaml_data)]
        yaml_data["clients"][0]["operationGroups"] = [
            self.update_operation_group(og) for og in yaml_data["operationGroups"]
        ]
        yaml_data["types"] = list(ORIGINAL_ID_TO_UPDATED_TYPE.values()) + list(
            KNOWN_TYPES.values()
        )
        if yaml_data.get("globalParameters"):
            del yaml_data["globalParameters"]
        del yaml_data["info"]
        del yaml_data["language"]
        del yaml_data["protocol"]
        del yaml_data["operationGroups"]
        if yaml_data.get("schemas"):
            del yaml_data["schemas"]
        if yaml_data.get("security"):
            del yaml_data["security"]
        ORIGINAL_ID_TO_UPDATED_TYPE.clear()
