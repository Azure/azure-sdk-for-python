# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import (
    Any,
    Callable,
    Optional,
    Type,
    Union,
    cast,
    Mapping,
    TYPE_CHECKING,
    Tuple,
    TypeVar,
    overload
)
import json
try:
    import jsonschema
except ImportError:
    jsonschema = None

from functools import partial


from ... import (  # pylint: disable=import-error
    MessageContent,
    MessageType as MessageTypeProtocol,
)
from ._exceptions import (  # pylint: disable=import-error
    InvalidContentError,
)
from ._constants import JSON_MIME_TYPE  # pylint: disable=import-error

if TYPE_CHECKING:
    try:
        from jsonschema.protocols import Validator
    except ImportError:
        pass
    from ._constants import JsonSchemaDraftIdentifier
    from ... import SchemaContentValidate

# TypeVar ties the return type to the exact MessageType class, rather than the "MessageType" Protocol
# Otherwise, mypy will complain that the return type is not compatible with the type annotation when
# the MessageType object is returned and passed around.
MessageType = TypeVar("MessageType", bound=MessageTypeProtocol)

def get_jsonschema_validator(
    draft_identifier: Union[str, "JsonSchemaDraftIdentifier"]
) -> "Validator":
    # get draft identifier string
    try:
        draft_identifier = cast("JsonSchemaDraftIdentifier", draft_identifier)
        draft_identifier = draft_identifier.value
    except AttributeError:
        pass

    # get validator
    try:
        validator = jsonschema.validators.validator_for(
            {"$schema": draft_identifier},
            default=False
        )
    except AttributeError:
        raise ValueError("To use a provided JSON Schema Validator, please install the " \
            "package with extras: `pip install azure-schemaregistry[jsonencoder]`.") from None

    if not validator:
        raise ValueError(f"{draft_identifier} is not a supported identifier. Please provide a supported " \
            "JsonSchemaDraftIdentifier value.")

    return partial(jsonschema_validate, validator=validator)

def jsonschema_validate(
    validator: "Validator",
    schema: Mapping[str, Any],
    content: Mapping[str, Any]
) -> None:
    """
    Validates content against provided schema using `jsonschema.Draft4Validator`.
     If invalid, raises Exception. Else, returns None.
     If jsonschema is not installed, raises ValueError.
     :param jsonschema.protocols.Validator validator: The validator to use.
     :param mapping[str, any] schema: The schema to validate against.
     :param mapping[str, any] content: The content to validate.
     :return: None
     :rtype: None
    """
    validator(schema).validate(content)

def get_loaded_schema(
    schema: Union[str, Callable],   # TODO: for next beta: check if we want to allow schema generation
    content: Mapping[str, Any],
) -> Tuple[str, str, Mapping[str, Any]]:
    """Returns the tuple: (schema name, schema string, schema dict).
    :param str or callable schema: The schema to load.
    :param mapping[str, any] content: The content to validate.
    :return: The schema name, schema string, and schema dict.
    :rtype: tuple[str, str, mapping[str, any]]
    """
    # get schema string
    schema_dict: Mapping[str, Any]
    schema_str: str
    schema_fullname: str
    try:
        # str
        schema = cast(str, schema)
        schema_dict = json.loads(schema)
        schema_str = schema
    except TypeError:
        # callable
        schema = cast(Callable, schema)
        try:
            schema_dict = schema(content)
        except Exception as exc:
            raise InvalidContentError(
                f"Cannot generate schema with callable given the following content: {content}"
            ) from exc
        schema_str = json.dumps(schema_dict)

    # get schema name for get_schema_properties operation
    try:
        schema_fullname = schema_dict['title']
    except KeyError:
        raise ValueError("Schema must have 'title' property.") from None

    return schema_fullname, schema_str, schema_dict

@overload
def create_message_content(
    content: Mapping[str, Any],
    schema: Mapping[str, Any],
    schema_id: str,
    validate: "Validator",
    message_type: Type[MessageType],
    **kwargs: Any,
) -> MessageType:
    ...

@overload
def create_message_content(
    content: Mapping[str, Any],
    schema: Mapping[str, Any],
    schema_id: str,
    validate: "Validator",
    message_type: None = None,
) -> MessageContent:
    ...

def create_message_content(
    content: Mapping[str, Any],
    schema: Mapping[str, Any],
    schema_id: str,
    validate: Union["Validator", "SchemaContentValidate"],
    message_type: Optional[Type[MessageType]] = None,
    **kwargs: Any,
) -> Union[MessageType, MessageContent]:
    content_type = f"{JSON_MIME_TYPE}+{schema_id}"
    try:
        # validate content
        validate(schema=schema, content=content)
    except Exception as exc:  # pylint:disable=broad-except
        raise InvalidContentError(
            f"Invalid content value '{content}' for the following schema with schema ID {schema_id}:"
            f"{json.dumps(schema)}",
            details={"schema_id": f"{schema_id}"},
    ) from exc

    try:
        content_bytes = json.dumps(content, separators=(',', ':')).encode()
    except Exception as exc:
        raise InvalidContentError(
            f"Cannot encode value '{content}' for the following schema with schema ID {schema_id}:"
            f"{json.dumps(schema)}",
            details={"schema_id": f"{schema_id}"},
        ) from exc

    if message_type:
        try:
            return cast(
                MessageType,
                message_type.from_message_content(content_bytes, content_type, **kwargs)
            )
        except AttributeError as exc:
            raise TypeError(
                f"""Cannot set content and content type on model object. The content model
                    {str(message_type)} must be a subtype of the MessageType protocol.
                    If using an Azure SDK model class, please check the README.md for the full list
                    of supported Azure SDK models and their corresponding versions.""",
                {"content": content_bytes, "content_type": content_type},
            ) from exc

    return MessageContent({"content": content_bytes, "content_type": content_type})


def parse_message(
    message: Union[MessageType, MessageContent]
):
    try:
        message = cast("MessageType", message)
        message_content_dict = message.__message_content__()
        content = message_content_dict["content"]
        content_type = message_content_dict["content_type"]
    except AttributeError:
        message = cast(MessageContent, message)
        try:
            content = message["content"]
            content_type = message["content_type"]
        except (KeyError, TypeError) as exc:
            raise TypeError(
                f"""The content model {str(message)} must be a subtype of the MessageType protocol or type
                    MessageContent. If using an Azure SDK model class, please check the README.md
                    for the full list of supported Azure SDK models and their corresponding versions."""
            ) from exc

    try:
        content_type_parts = content_type.split("+")
        if len(content_type_parts) != 2 or content_type_parts[0] != JSON_MIME_TYPE:
            raise InvalidContentError(
                f"Content type {content_type} was not in the expected format of JSON MIME type + schema ID."
            )
        schema_id = content_type_parts[1]
    except AttributeError:
        raise InvalidContentError(
            f"Content type {content_type} was not in the expected format of JSON MIME type + schema ID."
        ) from None

    return schema_id, content


def decode_content(
    content: bytes,
    schema_id: str,
    schema_definition: str,
    validate: Union["Validator", "SchemaContentValidate"],
):
    try:
        content = json.loads(content)
    except Exception as exc:
        error_message = (
            f"Cannot decode value '{content!r}' for schema with schema ID {schema_id}: {schema_definition}"
        )
        raise InvalidContentError(
            error_message,
            details={
                "schema_id": f"{schema_id}",
                "schema_definition": f"{schema_definition}",
            },
        ) from exc
    try:
        validate(
            schema=json.loads(schema_definition),
            content=cast(Mapping[str, Any], content)
        )
    except Exception as exc:
        error_message = (
            f"Invalid content value '{content!r}' for schema with schema ID {schema_id}: {schema_definition}"
        )
        raise InvalidContentError(
            error_message,
            details={
                "schema_id": f"{schema_id}",
                "schema_definition": f"{schema_definition}",
            },
        ) from exc
    return content
