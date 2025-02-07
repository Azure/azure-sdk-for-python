# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
from dataclasses import dataclass, is_dataclass, fields
import os
import re
import json
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from jinja2 import Template
from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from azure.ai.evaluation._constants import DefaultOpenEncoding
from azure.ai.evaluation.prompty._exceptions import (
    InvalidInputError,
    JinjaTemplateError,
    PromptyException,
)
from azure.ai.evaluation.prompty._image import Base64Image, FileImage, ImageBase, LazyUrlImage
from azure.ai.evaluation.prompty._yaml_utils import load_yaml


# region: Resolving references


@dataclass
class PromptyModelConfiguration:
    """
    A dataclass that represents a model config of prompty.

    :param api: Type of the LLM request, default value is chat.
    :type api: str
    :param configuration: Prompty model connection configuration
    :type configuration: dict
    :param parameters: Params of the LLM request.
    :type parameters: dict
    :param response: Return the complete response or the first choice, default value is first.
    :type response: str
    """

    configuration: dict
    parameters: Dict[str, Any]
    response: str = "first"
    model: Optional[str] = None
    # _overflow: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.configuration, dict):
            raise PromptyException("The configuration of the model must be a dictionary.")

        if not self.model:
            self.model = self.configuration.get("azure_deployment", None) or self.configuration.get("model", None)


T = TypeVar("T")


def dataclass_from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
    """Helper function to make creating dataclass instances from dictionaries easier.
    Unlike using cls(**data), this function will ignore any keys in the dictionary that
    are not fields in the dataclass. If the dataclass optionally contains an _overflow
    field, any extra key/value paris will be placed in that field.

    This does no type checking and inspects only the key names.

    :param Type[T] cls: The dataclass type to create.
    :param Dict[str, Any] data: The dictionary to create the dataclass instance from.
    :return: The dataclass instance.
    :rtype: T
    """
    if not is_dataclass(cls):
        raise ValueError("This function only works with @dataclass Types")

    fields_set: Set[str] = {f.name for f in fields(cls)}

    params: Dict[str, Any] = {}
    overflow: Dict[str, Any] = {}

    for key, value in data.items():
        if key in fields_set:
            params[key] = value
        else:
            overflow[key] = value

    if "_overflow" in fields_set:
        params["_overflow"] = overflow

    return cast(T, cls(**params))


def resolve_references(origin: Mapping[str, Any], base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Resolve all reference in the object.

    :param Mapping[str, Any] origin: The object to resolve.
    :param Path|None base_path: The base path to resolve the file reference.
    :return: The resolved object.
    :rtype: Dict[str, Any]
    """

    def _resolve_references(origin: Any, base_path: Optional[Path] = None) -> Any:
        if isinstance(origin, str):
            return _resolve_reference(origin, base_path=base_path)
        if isinstance(origin, list):
            return [_resolve_references(item, base_path=base_path) for item in origin]
        if isinstance(origin, dict):
            return {key: _resolve_references(value, base_path=base_path) for key, value in origin.items()}
        return origin

    return {k: _resolve_references(v, base_path=base_path) for k, v in origin.items()}


def _resolve_reference(reference: str, base_path: Optional[Path] = None) -> Union[str, dict]:
    """
    Resolve the reference, two types are supported, env, file.
    When the string format is ${env:ENV_NAME}, the environment variable value will be returned.
    When the string format is ${file:file_path}, return the loaded json object.

    :param str reference: The reference string.
    :param Path|None base_path: The base path to resolve the file reference.
    :return: The resolved reference.
    :rtype: str | dict
    """
    pattern = r"\$\{(\w+):(.*)\}"
    match = re.match(pattern, reference)
    if match:
        reference_type, value = match.groups()
        if reference_type == "env":
            return os.environ.get(value, reference)

        if reference_type == "file":
            if not Path(value).is_absolute() and base_path:
                path = Path(base_path) / value
            else:
                path = Path(value)

            if not path.exists():
                raise PromptyException(f"Cannot find the reference file {value}.")

            with open(path, "r", encoding=DefaultOpenEncoding.READ) as f:
                if path.suffix.lower() == ".json":
                    return json.load(f)
                if path.suffix.lower() in [".yml", ".yaml"]:
                    return load_yaml(f)
                return f.read()

        # TODO ralphe: logging?
        # logger.warning(f"Unknown reference type {reference_type}, return original value {reference}.")
        return reference

    return reference


def update_dict_recursively(origin_dict: Mapping[str, Any], overwrite_dict: Mapping[str, Any]) -> Dict[str, Any]:
    updated_dict: Dict[str, Any] = {}
    for k, v in overwrite_dict.items():
        if isinstance(v, dict):
            updated_dict[k] = update_dict_recursively(origin_dict.get(k, {}), v)
        else:
            updated_dict[k] = v
    for k, v in origin_dict.items():
        if k not in updated_dict:
            updated_dict[k] = v
    return updated_dict


# endregion


# region: Jinja template rendering

VALID_ROLES = ["system", "user", "assistant", "function"]
PROMPTY_ROLE_SEPARATOR_PATTERN = re.compile(
    r"(?i)^\s*#?\s*(" + "|".join(VALID_ROLES) + r")\s*:\s*\n", flags=re.MULTILINE
)
IMAGE_MATCH_PATTERN = re.compile(r"\!\[(\s*image\s*)\]\(\{\{(\s*[^\s{}]+\s*)\}\}\)")


def convert_prompt_template(template: str, inputs: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    prompt = _preprocess_template_string(template)
    reference_images = _find_referenced_image_set(inputs)
    rendered_prompt = _build_messages(prompt=prompt, images=reference_images, **inputs)
    return rendered_prompt


def render_jinja_template(template_str: str, *, trim_blocks=True, keep_trailing_newline=True, **kwargs) -> str:
    try:
        template = Template(template_str, trim_blocks=trim_blocks, keep_trailing_newline=keep_trailing_newline)
        return template.render(**kwargs)
    except Exception as e:  # pylint: disable=broad-except
        raise PromptyException(f"Failed to render jinja template - {type(e).__name__}: {str(e)}") from e


def _preprocess_template_string(template_string: str) -> str:
    """Remove the image input decorator from the template string and place the image input in a new line.

    :param str template_string: The template string.
    :return: The processed template string.
    :rtype: str
    """

    template_string = IMAGE_MATCH_PATTERN.sub(r"{{\1}}", template_string)
    return template_string


def _find_referenced_image_set(kwargs: Mapping) -> Set[ImageBase]:
    referenced_images: Set[ImageBase] = set()
    try:
        for _, value in kwargs.items():
            _add_referenced_images_to_set(value, referenced_images)
    except ImportError:
        pass
    return referenced_images


def _add_referenced_images_to_set(value: Any, image_set: Set[ImageBase]) -> None:
    if isinstance(value, ImageBase):
        image_set.add(value)
    elif isinstance(value, list):
        for item in value:
            _add_referenced_images_to_set(item, image_set)
    elif isinstance(value, dict):
        for _, item in value.items():
            _add_referenced_images_to_set(item, image_set)


def _build_messages(
    prompt: str,
    images: Iterable[ImageBase],
    image_detail: str = "auto",
    **kwargs,
) -> Sequence[Mapping[str, Any]]:
    # keep_trailing_newline=True is to keep the last \n in the prompt to avoid converting "user:\t\n" to "user:".
    chat_str = render_jinja_template(prompt, trim_blocks=True, keep_trailing_newline=True, **kwargs)
    messages = _parse_chat(chat_str, images=images, image_detail=image_detail)
    return messages


def _parse_chat(
    chat_str, images: Optional[Iterable[ImageBase]] = None, image_detail: str = "auto"
) -> Sequence[Mapping[str, Any]]:
    # openai chat api only supports VALID_ROLES as role names.
    # customer can add single # in front of role name for markdown highlight.
    # and we still support role name without # prefix for backward compatibility.

    images = images or []
    hash2images = {str(x): x for x in images}

    chunks = re.split(PROMPTY_ROLE_SEPARATOR_PATTERN, chat_str)
    chat_list: List[Dict[str, Any]] = []

    for chunk in chunks:
        last_message = chat_list[-1] if len(chat_list) > 0 else None

        # =======================================================================================================
        # NOTE: The Promptflow code supported tool calls but used eval() to parse them. This is an unacceptable
        #       security risk. Since none of the current evaluators use tool calls, this functionality has been
        #       removed.
        # =======================================================================================================

        # if is_tool_chunk(last_message):
        #     parse_tools(last_message, chunk, hash2images, image_detail)
        #     continue
        # if last_message and "role" in last_message and last_message["role"] == "assistant":
        #     parsed_result = _try_parse_tool_calls(chunk)
        #     if parsed_result is not None:
        #         last_message["tool_calls"] = parsed_result
        #         continue

        if (
            last_message
            and "role" in last_message  # pylint: disable=unsupported-membership-test
            and "content" not in last_message  # pylint: disable=unsupported-membership-test
            and "tool_calls" not in last_message  # pylint: disable=unsupported-membership-test
        ):
            parsed_result = _try_parse_name_and_content(chunk)
            if parsed_result is None:
                if last_message["role"] == "function":  # pylint: disable=unsubscriptable-object
                    # "name" is required if the role is "function"
                    raise JinjaTemplateError(
                        "Failed to parse function role prompt. Please make sure the prompt follows the "
                        "format: 'name:\\nfunction_name\\ncontent:\\nfunction_content'. "
                        "'name' is required if role is function, and it should be the name of the function "
                        "whose response is in the content. May contain a-z, A-Z, 0-9, and underscores, "
                        "with a maximum length of 64 characters. See more details in "
                        "https://platform.openai.com/docs/api-reference/chat/create#chat/create-name"
                    )

                # "name" is optional for other role types.
                last_message["content"] = to_content_str_or_list(  # pylint: disable=unsupported-assignment-operation
                    chunk, hash2images, image_detail
                )
            else:
                last_message["name"] = parsed_result[0]  # pylint: disable=unsupported-assignment-operation
                last_message["content"] = to_content_str_or_list(  # pylint: disable=unsupported-assignment-operation
                    parsed_result[1], hash2images, image_detail
                )
        else:
            if chunk.strip() == "":
                continue
            # Check if prompt follows chat api message format and has valid role.
            # References: https://platform.openai.com/docs/api-reference/chat/create.
            role = chunk.strip().lower()
            _validate_role(role)
            new_message = {"role": role}
            chat_list.append(new_message)
    return chat_list


def _validate_role(role: str):
    if role not in VALID_ROLES:
        valid_roles_str = ", ".join(VALID_ROLES)
        error_message = (
            f"The Chat API requires a specific format for prompt definition, and the prompt should include separate "
            f"lines as role delimiters: {valid_roles_str}.\n"
            f"Current parsed role '{role}' does not meet the requirement. If you intend to use the Completion API, "
            f"please select the appropriate API type and deployment name."
        )
        raise JinjaTemplateError(message=error_message)


def to_content_str_or_list(
    chat_str: str, hash2images: Mapping[str, ImageBase], image_detail: str
) -> Union[str, List[Dict[str, Any]]]:
    chat_str = chat_str.strip()
    chunks = chat_str.split("\n")
    include_image = False
    result = []

    for chunk in chunks:
        chunk = chunk.strip()

        if not chunk:
            continue

        if (img := hash2images.get(chunk)) is not None:
            image_url = img.as_url()
            image_message = {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": image_detail,
                },
            }
            result.append(image_message)
            include_image = True
        else:
            result.append({"type": "text", "text": chunk})

    return result if include_image else chat_str


def _try_parse_name_and_content(role_prompt: str) -> Optional[Tuple[str, str]]:
    # customer can add ## in front of name/content for markdown highlight.
    # and we still support name/content without ## prefix for backward compatibility.
    pattern = r"\n*#{0,2}\s*name\s*:\s*\n+\s*(\S+)\s*\n*#{0,2}\s*content\s*:\s*\n?(.*)"
    match = re.search(pattern, role_prompt, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None


# endregion


# region: Image parsing

MIME_PATTERN = re.compile(r"^data:image/(.*);(path|base64|url):\s*(.*)$")


def get_image_obj(image_str: str, working_dir: Path) -> Union[str, ImageBase]:
    match = re.match(MIME_PATTERN, image_str)
    if match:
        mime_type, image_type, image_content = f"image/{match.group(1)}", match.group(2), match.group(3)
        if image_type == "path":
            image_path = Path(image_content)
            if not image_path.is_absolute():
                image_path = Path(working_dir) / image_content
            if not image_path.exists():
                # TODO ralphe logging? Code threw a different exception initially
                # logger.warning(f"Cannot find the image path {image_content},
                #                  it will be regarded as {type(image_str)}.")
                raise InvalidInputError(f"Cannot find the image path '{image_path.as_posix()}'")
            return FileImage(image_path, mime_type)

        if image_type == "base64":
            # TODO ralphe: do we need to do image_content=image_content.split(",")[-1] ??
            return Base64Image(image_content, mime_type)

        if image_type == "url":
            return LazyUrlImage(image_content, mime_type)

        # TODO ralphe logging? Code did not throw an exception originally
        # logger.warning(f"Invalid mine type {mime_type}, it will be regarded as {type(image_str)}.")
        raise InvalidInputError(f"Image input format invalid or not supported '{match.group()}'")
    return image_str


# endregion


# region OpenAI connections and requests

OpenAIChatResponseType = Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]


def prepare_open_ai_request_params(
    model_config: PromptyModelConfiguration, template: Union[str, Sequence[Mapping[str, Any]]]
) -> MutableMapping[str, Any]:
    params = copy.deepcopy(model_config.parameters)
    # if isinstance(connection, AzureOpenAIConnection):
    #     params.setdefault("extra_headers", {}).update({"ms-azure-ai-promptflow-called-from": "promptflow-core"})
    params["model"] = model_config.model
    params["messages"] = template

    # NOTE:
    # - Tool calls have been disabled due to a security issue in the implementation. See comment earlier in
    #   this file for more details
    # - Removing the validation of function calls in favour of letting the service do that validation. This
    #   removes a maintenance burden from the SDK should the service definition for function calls change.

    # # functions and function_call are deprecated and are replaced by tools and tool_choice.
    # # if both are provided, tools and tool_choice are used and functions and function_call are ignored.
    # if "tools" in params:
    #     validate_tools(params["tools"])
    #     params["tool_choice"] = validate_tool_choice(params.get("tool_choice", None))
    # else:
    #     if "functions" in params:
    #         _validate_functions(params["functions"])
    #         params["function_call"] = validate_function_call(params.get("function_call", None))

    return params


async def format_llm_response(
    response: OpenAIChatResponseType,
    is_first_choice: bool,
    response_format: Optional[Mapping[str, Any]] = None,
    outputs: Optional[Mapping[str, Any]] = None,
) -> Union[OpenAIChatResponseType, AsyncGenerator[str, None], str, Mapping[str, Any]]:
    """
    Format LLM response

    If is_first_choice is false, it will directly return LLM response.
    If is_first_choice is true, behavior as blow:
        response_format: type: text
            - n: None/1/2
                Return the first choice content. Return type is string.
            - stream: True
                Return generator list of first choice content. Return type is generator[str]
        response_format: type: json_object
            - n : None/1/2
                Return json dict of the first choice. Return type is dict
            - stream: True
                Return json dict of the first choice. Return type is dict
            - outputs
                Extract corresponding output in the json dict to the first choice. Return type is dict.

    :param response: LLM response.
    :type response:
    :param is_first_choice: If true, it will return the first item in response choices, else it will return all response
    :type is_first_choice: bool
    :param response_format: An object specifying the format that the model must output.
    :type response_format: str
    :param outputs: Extract corresponding output in json format response
    :type outputs: dict
    :return: Formatted LLM response.
    :rtype: Union[str, dict, Response]
    """

    def format_choice(item: str) -> Union[str, Mapping[str, Any]]:
        # response_format is one of text or json_object.
        # https://platform.openai.com/docs/api-reference/chat/create#chat-create-response_format
        if is_json_format:
            result_dict = json.loads(item)
            if not outputs:
                return result_dict
            # return the keys in outputs
            output_results = {}
            for key in outputs:
                if key not in result_dict:
                    raise InvalidInputError(f"Cannot find {key} in response {list(result_dict.keys())}")
                output_results[key] = result_dict[key]
            return output_results
        # Return text format response
        return item

    async def format_stream(llm_response: AsyncStream[ChatCompletionChunk]) -> AsyncGenerator[str, None]:
        cur_index = None
        async for chunk in llm_response:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                if cur_index is None:
                    cur_index = chunk.choices[0].index
                if cur_index != chunk.choices[0].index:
                    return
                yield chunk.choices[0].delta.content

    if not is_first_choice:
        return response

    is_json_format = isinstance(response_format, dict) and response_format.get("type") == "json_object"
    if isinstance(response, AsyncStream):
        if not is_json_format:
            return format_stream(llm_response=response)
        content = "".join([item async for item in format_stream(llm_response=response)])
        return format_choice(content)

    # When calling function/tool, function_call/tool_call response will be returned as a field in message,
    # so we need return message directly. Otherwise, we only return content.
    # https://platform.openai.com/docs/api-reference/chat/object#chat/object-choices
    if response.choices[0].finish_reason in ["tool_calls", "function_calls"]:
        response_content = response.model_dump()["choices"][0]["message"]
    else:
        response_content = getattr(response.choices[0].message, "content", "")
    result = format_choice(response_content)
    return result


# endregion
