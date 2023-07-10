# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, AsyncBearerTokenCredentialPolicy

DEFAULT_AUDIENCE = "https://search.azure.com"


def is_retryable_status_code(status_code: int) -> bool:
    return status_code in [422, 409, 503]


def get_authentication_policy(credential, *, is_async: bool = False, **kwargs):
    audience = kwargs.get("audience", None)
    if not audience:
        audience = DEFAULT_AUDIENCE
    scope = audience.rstrip("/") + "/.default"
    _policy = BearerTokenCredentialPolicy if not is_async else AsyncBearerTokenCredentialPolicy
    authentication_policy = _policy(credential, scope)
    return authentication_policy


def odata(statement: str, **kwargs: Any) -> str:
    """Escape an OData query string.

    The statement to prepare should include fields to substitute given inside
    braces, e.g. `{somevar}` and then pass the corresponding value as a keyword
    argument, e.g. `somevar=10`.

    :param statement: An OData query string to prepare
    :type statement: str
    :return: The prepared OData query string
    :rtype: str

    .. admonition:: Example:

        >>> odata("name eq {name} and age eq {age}", name="O'Neil", age=37)
        "name eq 'O''Neil' and age eq 37"


    """
    for key, value in kwargs.items():
        if isinstance(value, str):
            value = value.replace("'", "''")
            if f"'{{{key}}}'" not in statement:
                kwargs[key] = f"'{value}'"
    return statement.format(**kwargs)
