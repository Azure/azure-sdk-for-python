# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Mapping, Optional
from openai import OpenAIError
from azure.ai.evaluation._exceptions import ErrorCategory, ErrorBlame, ErrorTarget, EvaluationException

_KNOWN_FINISH_REASONS = ("stop", "length", "content_filter", "tool_calls", "function_call")

# Fixed causes for InvalidLLMOutputError. They must never include model output.
RESPONSE_TRUNCATED = "the model response was truncated at the output token limit"
RESPONSE_CONTENT_FILTERED = "the model response was blocked by the content filter"
RESPONSE_EMPTY = "the model returned an empty response"
RESPONSE_NOT_JSON = "the model response was not valid JSON"
RESPONSE_NOT_JSON_OBJECT = "the model response was not a JSON object"
RESPONSE_UNEXPECTED_TYPE = "the model response had unexpected type {}"
RESPONSE_NO_VALID_SCORE = "the model response had no valid numeric score"

_USAGE_KEYS = ("prompt_tokens", "completion_tokens", "total_tokens")


def _known_count(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def invalid_llm_output_message(
    cause: str, finish_reason: Any = None, output_tokens: Any = None, subject: str = "Model"
) -> str:
    """Build an actionable invalid model output message from non-content metadata only.

    :param cause: A fixed description of why the output was unusable. Must not contain model output.
    :type cause: str
    :param finish_reason: The completion finish reason. Unrecognized values are reported as ``unknown``.
    :type finish_reason: Any
    :param output_tokens: The completion token count. Non-integer values are reported as ``unknown``.
    :type output_tokens: Any
    :param subject: What returned the output, such as ``Model`` or ``Evaluator``.
    :type subject: str
    :return: The error message.
    :rtype: str
    """
    if finish_reason not in _KNOWN_FINISH_REASONS:
        finish_reason = "unknown"
    output_tokens = _known_count(output_tokens)
    return (
        f"{subject} returned invalid output: {cause} "
        f"(finish_reason={finish_reason}, output_tokens={'unknown' if output_tokens is None else output_tokens})."
    )


class PromptyException(EvaluationException):
    """Exception class for Prompty related errors.

    This exception is used to indicate that the error was caused by Prompty execution.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.UNKNOWN)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)

        super().__init__(message, **kwargs)


class MissingRequiredInputError(PromptyException):
    """Exception raised when missing required input"""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.MISSING_FIELD)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class InvalidInputError(PromptyException):
    """Exception raised when an input is invalid, could not be loaded, or is not the expected format."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class JinjaTemplateError(PromptyException):
    """Exception raised when the Jinja template is invalid or could not be rendered."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class NotSupportedError(PromptyException):
    """Exception raised when the operation is not supported."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.UNKNOWN)
        kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
        super().__init__(message, **kwargs)


class InvalidLLMOutputError(PromptyException):
    """Exception raised when the LLM response cannot be used, such as when it cannot be parsed as requested.

    The message is built only from ``cause`` and response metadata, never from the model output. The known token
    usage and model name are kept in ``properties`` so that a failed result row can still report them.

    :param cause: A fixed description of why the output was unusable. Must not contain model output.
    :type cause: str
    :keyword finish_reason: The completion finish reason.
    :paramtype finish_reason: Any
    :keyword usage: The response's ``prompt_tokens``, ``completion_tokens``, ``total_tokens`` and ``model``.
    :paramtype usage: Optional[Mapping[str, Any]]
    :keyword subject: What returned the output, such as ``Model`` or ``Evaluator``.
    :paramtype subject: str
    """

    def __init__(
        self,
        cause: str,
        *,
        finish_reason: Any = None,
        usage: Optional[Mapping[str, Any]] = None,
        subject: str = "Model",
        **kwargs,
    ):
        usage = usage or {}
        self.cause = cause
        self.finish_reason = finish_reason
        self.usage = dict(usage)
        self.subject = subject
        message = invalid_llm_output_message(cause, finish_reason, usage.get("completion_tokens"), subject)
        properties: Dict[str, Any] = {
            key: usage[key] for key in _USAGE_KEYS if _known_count(usage.get(key)) is not None
        }
        model = usage.get("model")
        if isinstance(model, str) and model.strip():
            properties["model"] = model
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        # A response withheld by the content filter is caused by the evaluated content, as a filtered prompt is.
        kwargs.setdefault(
            "blame", ErrorBlame.USER_ERROR if finish_reason == "content_filter" else ErrorBlame.SYSTEM_ERROR
        )
        kwargs.setdefault("internal_message", message)
        kwargs.setdefault("properties", properties)
        super().__init__(message, **kwargs)

    def for_evaluator(self) -> "InvalidLLMOutputError":
        """Return the same error worded as an evaluator's.

        :return: The error with the subject ``Evaluator``.
        :rtype: InvalidLLMOutputError
        """
        if self.subject == "Evaluator":
            return self
        return InvalidLLMOutputError(
            self.cause,
            finish_reason=self.finish_reason,
            usage=self.usage,
            subject="Evaluator",
            category=self.category,
            target=self.target,
            blame=self.blame,
            properties=self.properties,
        )


class WrappedOpenAIError(PromptyException):
    """Exception raised when an OpenAI error is encountered."""

    def __init__(self, *, message: Optional[str] = None, error: Optional[OpenAIError] = None, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)

        message = (
            message or self.to_openai_error_message(error)
            if error
            else "An error occurred while executing the OpenAI API."
        )
        super().__init__(message, **kwargs)

    @staticmethod
    def to_openai_error_message(e: OpenAIError) -> str:
        # TODO ralphe: Error handling that relies on string matching is fragile and should be replaced
        #              with a more robust solution that examines the actual error type since that provies
        #              more than enough information to handle errors.
        ex_type = type(e).__name__
        error_message = str(e)
        # https://learn.microsoft.com/en-gb/azure/ai-services/openai/reference
        if error_message == "<empty message>":
            msg = "The api key is invalid or revoked. " "You can correct or regenerate the api key of your connection."
            return f"OpenAI API hits {ex_type}: {msg}"
        # for models that do not support the `functions` parameter.
        elif "Unrecognized request argument supplied: functions" in error_message:
            msg = (
                "Current model does not support the `functions` parameter. If you are using openai connection, then "
                "please use gpt-3.5-turbo, gpt-4, gpt-4-32k, gpt-3.5-turbo-0613 or gpt-4-0613. You can refer to "
                "https://platform.openai.com/docs/guides/gpt/function-calling. If you are using azure openai "
                "connection, then please first go to your Azure OpenAI resource, deploy model 'gpt-35-turbo' or "
                "'gpt-4' with version 0613. You can refer to "
                "https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling."
            )
            return f"OpenAI API hits {ex_type}: {msg}"
        elif "Invalid content type. image_url is only supported by certain models" in error_message:
            msg = (
                "Current model does not support the image input. If you are using openai connection, then please use "
                "gpt-4-vision-preview. You can refer to https://platform.openai.com/docs/guides/vision."
                "If you are using azure openai connection, then please first go to your Azure OpenAI resource, "
                'create a GPT-4 Turbo with Vision deployment by selecting model name: "gpt-4" and '
                'model version "vision-preview". You can refer to '
                "https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision"
            )
            return f"OpenAI API hits {ex_type}: {msg}"
        elif (
            "'response_format' of type" in error_message and "is not supported with this model." in error_message
        ) or (
            "Additional properties are not allowed" in error_message
            and "unexpected) - 'response_format'" in error_message
        ):
            msg = (
                'The response_format parameter needs to be a dictionary such as {"type": "text"}. '
                "The value associated with the type key should be either 'text' or 'json_object' "
                'If you are using openai connection, you can only set response_format to { "type": "json_object" } '
                "when calling gpt-3.5-turbo-1106 or gpt-4-1106-preview to enable JSON mode. You can refer to "
                "https://platform.openai.com/docs/guides/text-generation/json-mode. If you are using azure openai "
                "connection, then please first go to your Azure OpenAI resource, compatible with GPT-4 Turbo and "
                "all GPT-3.5 Turbo models newer than gpt-35-turbo-1106. You can refer to "
                "https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/json-mode?tabs=python."
            )
            return f"OpenAI API hits {ex_type}: {msg}"
        elif "Principal does not have access to API/Operation" in error_message:
            msg = (
                "Principal does not have access to API/Operation. If you are using azure openai connection, "
                "please make sure you have proper role assignment on your azure openai resource. You can refer to "
                "https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control"
            )
            return f"OpenAI API hits {ex_type}: {msg}"
        else:
            return (
                f"OpenAI API hits {ex_type}: {error_message} [Error reference: "
                "https://platform.openai.com/docs/guides/error-codes/api-errors]"
            )
