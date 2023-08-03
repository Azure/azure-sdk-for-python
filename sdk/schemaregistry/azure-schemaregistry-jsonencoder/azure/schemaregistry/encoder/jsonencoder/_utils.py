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
    TypeVar,
    Mapping,
    TYPE_CHECKING,
    Tuple
)
import json

from ._exceptions import (  # pylint: disable=import-error
    InvalidContentError,
)
from ._message_protocol import (  # pylint: disable=import-error
    MessageContent,
    MessageType as MessageTypeProtocol,
)
from ._constants import (  # pylint: disable=import-error
    JSON_MIME_TYPE,
)
if TYPE_CHECKING:
    from logging import Logger
    from ._schema_registry_json_encoder import JsonSchemaEncoder
    from .aio._schema_registry_json_encoder_async import JsonSchemaEncoder as JsonSchemaEncoderAsync

MessageType = TypeVar("MessageType", bound=MessageTypeProtocol)

def load_schema(
    encoder: Union["JsonSchemaEncoder", "JsonSchemaEncoderAsync"],
    schema: Union[str, Callable],
    content: Mapping[str, Any],
) -> Tuple[str, str, Mapping[str, Any]]:
    """Returns the tuple: (schema name, schema string, schema dict).
    """

    # get schema string
    try:
        # str or bytes
        schema_dict = json.loads(schema)
        schema_str = schema
    except TypeError:
        # callable
        encoder._auto_register_schema_func = encoder._schema_registry_client.register_schema    # pylint: disable=protected-access
        try:
            schema_dict = schema(content)
        except Exception as exc:
            raise InvalidContentError(
                f"Cannot generate schema with callable given the following content: {content}"
            ) from exc
        schema_str = json.dumps(schema_dict)

    # get schema name for client operation
    try:
        schema_fullname = schema_dict['title']
    except KeyError:
        raise ValueError("Schema must have 'title' property.")

    return schema_fullname, schema_str, schema_dict

def create_message_content(
    validate: Callable,
    content: Mapping[str, Any],
    schema: Mapping[str, Any],
    schema_id: str,
    message_type: Optional[Type[MessageType]] = None,
    **kwargs: Any,
) -> Union[MessageType, MessageContent]:
    content_type = f"{JSON_MIME_TYPE}+{schema_id}"

    if validate:
        try:
            # validate content
            validate(content, schema)
        except Exception as exc:  # pylint:disable=broad-except
            raise InvalidContentError(
                f"Invalid content value '{content}' for the following schema with schema ID {schema_id}:"
                f"{json.dumps(schema)}",
                details={"schema_id": f"{schema_id}"},
        ) from exc

    try:
        content_bytes = json.dumps(content).encode()
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
    content: bytes,
    schema_id: str,
    schema_definition: str,
    validate: Optional[Callable],
):
    if validate:
        try:
            validate(json.loads(content), json.loads(schema_definition))
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
    return content
