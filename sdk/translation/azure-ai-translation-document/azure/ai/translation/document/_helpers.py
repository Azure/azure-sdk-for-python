# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
from typing import Union, Optional, List
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.pipeline.policies import HttpLoggingPolicy
from ._generated.models import (
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    TargetInput as _TargetInput,
    DocumentFilter as _DocumentFilter,
)
from ._models import DocumentTranslationInput

COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"
POLLING_INTERVAL = 1


def get_translation_input(args, kwargs, continuation_token):
    try:
        inputs = kwargs.pop("inputs", None)
        if not inputs:
            inputs = args[0]
        request = (
            DocumentTranslationInput._to_generated_list(  # pylint: disable=protected-access
                inputs
            )
            if not continuation_token
            else None
        )
    except (AttributeError, TypeError, IndexError):
        try:
            source_url = kwargs.pop("source_url", None)
            if not source_url:
                source_url = args[0]
            target_url = kwargs.pop("target_url", None)
            if not target_url:
                target_url = args[1]
            target_language = kwargs.pop("target_language", None)
            if not target_language:
                target_language = args[2]

            # Additional kwargs
            source_language = kwargs.pop("source_language", None)
            prefix = kwargs.pop("prefix", None)
            suffix = kwargs.pop("suffix", None)
            storage_type = kwargs.pop("storage_type", None)
            category_id = kwargs.pop("category_id", None)
            glossaries = kwargs.pop("glossaries", None)

            request = [
                _BatchRequest(
                    source=_SourceInput(
                        source_url=source_url,
                        filter=_DocumentFilter(
                            prefix=prefix,
                            suffix=suffix
                        ),
                        language=source_language,
                    ),
                    targets=[
                        _TargetInput(
                            target_url=target_url,
                            language=target_language,
                            glossaries=[g._to_generated() for g in glossaries]  # pylint: disable=protected-access
                            if glossaries else None,
                            category=category_id,
                        )
                    ],
                    storage_type=storage_type
                )
            ]
        except (AttributeError, TypeError, IndexError):
            raise ValueError(
                "Pass 'inputs' for multiple inputs or 'source_url', 'target_url', "
                "and 'target_language' for a single input."
            )

    return request


def get_authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name=COGNITIVE_KEY_HEADER, credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )

    return authentication_policy


def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "Operation-Location",
            "Content-Encoding",
            "Vary",
            "apim-request-id",
            "X-RequestId",
            "Set-Cookie",
            "X-Powered-By",
            "Strict-Transport-Security",
            "x-content-type-options",
        }
    )
    http_logging_policy.allowed_query_params.update(
        {
            "$top",
            "$skip",
            "$maxpagesize",
            "ids",
            "statuses",
            "createdDateTimeUtcStart",
            "createdDateTimeUtcEnd",
            "$orderBy",
        }
    )
    return http_logging_policy


def convert_datetime(date_time):
    # type: (Union[str, datetime.datetime]) -> datetime.datetime
    if isinstance(date_time, datetime.datetime):
        return date_time
    if isinstance(date_time, str):
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    raise TypeError("Bad datetime type")


def convert_order_by(order_by):
    # type: (Optional[List[str]]) -> Optional[List[str]]
    if order_by:
        order_by = [order.replace("created_on", "createdDateTimeUtc") for order in order_by]
    return order_by
