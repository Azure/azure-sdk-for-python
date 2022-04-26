# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Type, Union, cast
from avro.errors import SchemaResolutionException  # type: ignore

from ._exceptions import (  # pylint: disable=import-error
    InvalidContentError,
    InvalidSchemaError,
)
from ._message_protocol import (  # pylint: disable=import-error
    MessageContent,
    MessageType,
)
from ._constants import (  # pylint: disable=import-error
    AVRO_MIME_TYPE,
)

if TYPE_CHECKING:
    from ._apache_avro_encoder import (  # pylint: disable=import-error
        ApacheAvroObjectEncoder as AvroObjectEncoder,
    )


def validate_schema(avro_encoder: "AvroObjectEncoder", raw_input_schema: str):
    try:
        return avro_encoder.get_schema_fullname(raw_input_schema)
    except Exception as exc:  # pylint:disable=broad-except
        raise InvalidSchemaError(f"Cannot parse schema: {raw_input_schema}") from exc


def create_message_content(
    avro_encoder: "AvroObjectEncoder",
    content: Mapping[str, Any],
    raw_input_schema: str,
    schema_id: str,
    message_type: Optional[Type[MessageType]] = None,
    **kwargs: Any,
) -> Union[MessageType, MessageContent]:
    content_type = f"{AVRO_MIME_TYPE}+{schema_id}"

    try:
        content_bytes = avro_encoder.encode(content, raw_input_schema)
    except Exception as exc:  # pylint:disable=broad-except
        raise InvalidContentError(
            f"Cannot encode value '{content}' for the following schema with schema ID {schema_id}:"
            f"{raw_input_schema}",
            details={"schema_id": f"{schema_id}"},
        ) from exc

    stream = BytesIO()

    stream.write(content_bytes)
    stream.flush()

    payload = stream.getvalue()
    stream.close()

    if message_type:
        try:
            return message_type.from_message_content(payload, content_type, **kwargs)
        except AttributeError as exc:
            raise TypeError(
                f"""Cannot set content and content type on model object. The content model
                    {str(message_type)} must be a subtype of the MessageType protocol.
                    If using an Azure SDK model class, please check the README.md for the full list
                    of supported Azure SDK models and their corresponding versions.""",
                {"content": payload, "content_type": content_type},
            ) from exc

    return MessageContent({"content": payload, "content_type": content_type})


def validate_message(message: Union[MessageType, MessageContent]):
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
        if len(content_type_parts) != 2 or content_type_parts[0] != AVRO_MIME_TYPE:
            raise InvalidContentError(
                f"Content type {content_type} was not in the expected format of Avro MIME type + schema ID."
            )
        schema_id = content_type_parts[1]
    except AttributeError:
        raise InvalidContentError(
            f"Content type {content_type} was not in the expected format of Avro MIME type + schema ID."
        )

    return schema_id, content


def decode_content(
    avro_encoder: "AvroObjectEncoder",
    content: bytes,
    schema_id: str,
    schema_definition: str,
    readers_schema: Optional[str] = None,
):
    try:
        reader = avro_encoder.get_schema_reader(schema_definition, readers_schema)
    except Exception as exc:
        error_message = (
            f"Invalid schema for the following writer's schema with schema ID {schema_id}:"
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
        ) from exc

    try:
        dict_value = avro_encoder.decode(content, reader)  # type: Dict[str, Any]
    except SchemaResolutionException as exc:
        raise InvalidSchemaError(
            f"Incompatible schemas.\nWriter's Schema: {schema_definition}\nReader's Schema: {readers_schema}",
            details={
                "schema_id": f"{schema_id}",
                "schema_definition": f"{schema_definition}",
            },
        ) from exc
    except Exception as exc:  # pylint:disable=broad-except
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
    return dict_value
