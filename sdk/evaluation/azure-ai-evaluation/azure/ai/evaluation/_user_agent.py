# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Iterator

from azure.ai.evaluation._version import VERSION

# Validate that VERSION is not empty or None to prevent unauthorized SDK usage
# This is specifically important for red teaming scenarios
if not VERSION or not isinstance(VERSION, str) or not VERSION.strip():
    raise ValueError("Invalid SDK version: version must be a non-empty string")


class UserAgentSingleton:
    __BASE_USER_AGENT: str = "{}/{}".format("azure-ai-evaluation", VERSION)

    @property
    def value(self):
        """Get the user-agent"""
        return self.__BASE_USER_AGENT

    def __str__(self) -> str:
        return self.value

    @classmethod
    @contextmanager
    def add_useragent_product(cls, *product: str) -> Iterator[None]:
        """Appends a "product" (e.g. `name/version`) to the base user agent

        :param product: User Agent products to append to the base user agent

         ..see-also::

             `User-Agent section of RFC 9110, <https://www.rfc-editor.org/rfc/rfc9110#name-user-agent>`
        """
        old_useragent = cls.__BASE_USER_AGENT
        cls.__BASE_USER_AGENT = f"{old_useragent} {' '.join(product)}"

        yield

        cls.__BASE_USER_AGENT = old_useragent
