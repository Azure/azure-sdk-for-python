# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Iterator

from azure.ai.evaluation._version import VERSION


class UserAgentSingleton:
    __BASE_USER_AGENT: str = "{}/{}".format("azure-ai-evaluation", VERSION)
    __REDTEAM_USER_AGENT: str = "{}-redteam/{}".format("azure-ai-evaluation", VERSION)
    __is_redteam_context: bool = False

    @property
    def value(self):
        """Get the user-agent"""
        return self.__REDTEAM_USER_AGENT if self.__is_redteam_context else self.__BASE_USER_AGENT

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

    @classmethod
    @contextmanager
    def redteam_context(cls) -> Iterator[None]:
        """Context manager to use red team user agent for RAI service calls

        This context manager temporarily sets the user agent to "azure-ai-evaluation-redteam"
        for all calls within the context.
        """
        old_context = cls.__is_redteam_context
        cls.__is_redteam_context = True

        yield

        cls.__is_redteam_context = old_context
