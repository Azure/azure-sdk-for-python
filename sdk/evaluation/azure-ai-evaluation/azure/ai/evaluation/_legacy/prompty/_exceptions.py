# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional
from openai import OpenAIError
from azure.ai.evaluation._exceptions import ErrorCategory, ErrorBlame, ErrorTarget, EvaluationException


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
