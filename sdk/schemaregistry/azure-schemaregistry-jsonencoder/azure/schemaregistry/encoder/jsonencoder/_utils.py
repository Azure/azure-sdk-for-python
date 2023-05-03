# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    Type,
    Union,
    cast,
    TypeVar,
    Mapping
)
import json
import jsonschema
from jsonschema.exceptions import ValidationError, SchemaError

from ._exceptions import (  # pylint: disable=import-error
    InvalidContentError,
    InvalidSchemaError,
)
from ._message_protocol import (  # pylint: disable=import-error
    MessageContent,
    MessageType as MessageTypeProtocol,
)
from ._constants import (  # pylint: disable=import-error
    JSON_MIME_TYPE,
)
if TYPE_CHECKING:
    from jsonschema.protocols import Validator

MessageType = TypeVar("MessageType", bound=MessageTypeProtocol)


def validate_schema(
    schema: Mapping[str, Any],
    json_validator: "Validator"
) -> None:
    try:    # returns None if valid schema
        json_validator.check_schema(schema=schema)
    except SchemaError as exc:  # pylint:disable=broad-except
        raise InvalidSchemaError(f"Cannot parse schema: {schema}") from exc


def create_message_content(
    json_validator: "Validator",
    content: Mapping[str, Any],
    schema: Mapping[str, Any],
    schema_id: str,
    message_type: Optional[Type[MessageType]] = None,
    **kwargs: Any,
) -> Union[MessageType, MessageContent]:
    content_type = f"{JSON_MIME_TYPE}+{schema_id}"

    try:
        # validate content
        json_validator(schema).validate(content)
        content_bytes = json.dumps(content).encode()
    except ValidationError as exc:  # pylint:disable=broad-except
        raise InvalidContentError(
            f"Cannot encode value '{content}' for the following schema with schema ID {schema_id}:"
            f"{json.dumps(schema)}",
            details={"schema_id": f"{schema_id}"},
        ) from exc

    if message_type:
        try:
            return cast(
                MessageType,
                message_type.from_message_content(content_bytes, content_type, **kwargs),
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
        message = cast(MessageType, message)
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
        )

    return schema_id, content


def decode_content(
    json_validator: "Validator",
    content: bytes,
    schema_id: str,
    schema_definition: str,
    readers_schema: Optional[str] = None,
):
    if readers_schema and readers_schema != schema_definition:
        error_message = (
            f"Reader's schema does not match the writer's schema with schema ID {schema_id}:"
            f"{schema_definition}\nand readers schema: {readers_schema}"
            if readers_schema
            else f"Invalid schema for the following writer's schema with schema ID {schema_id}: {schema_definition}"
        )
        raise InvalidSchemaError(
            error_message,
            details={
                "schema_id": f"{schema_id}",
                "schema_definition": f"{schema_definition}",
            },
        )

    try:
        json_validator(json.loads(schema_definition)).validate(json.loads(content))
    except ValidationError as exc:
        error_message = (
            f"Cannot decode value '{content!r}' for the following schema with schema ID {schema_id}:"
            f"{schema_definition}\nand readers schema: {readers_schema}"
            if readers_schema
            else f"Cannot decode value '{content!r}' for schema with schema ID {schema_id}: {schema_definition}"
        )
        raise InvalidContentError(
            error_message,
            details={
                "schema_id": f"{schema_id}",
                "schema_definition": f"{schema_definition}",
            },
        ) from exc
    return content
