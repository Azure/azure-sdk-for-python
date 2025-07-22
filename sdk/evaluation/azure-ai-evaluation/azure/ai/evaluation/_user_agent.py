# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Iterator

from azure.ai.evaluation._version import VERSION


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

    @classmethod
    @contextmanager
    def redteam_context(cls, *, subtype: str = "RedTeam", **kwargs) -> Iterator[None]:
        """Context manager to use red team user agent for RAI service calls

        This context manager temporarily sets the user agent to include red team context
        for all calls within the context.

        :param subtype: The subtype to use in the red team user agent. Defaults to "RedTeam"
        :type subtype: str
        :param kwargs: Additional keyword arguments for future extensibility
        """
        with cls.add_useragent_product(f"(type=redteam; subtype={subtype})"):
            yield

    @classmethod
    @contextmanager
    def redteam_context_with_product(cls, *products: str) -> Iterator[None]:
        """Context manager to use custom red team user agent for RAI service calls

        This context manager temporarily sets the user agent to include custom red team
        products for all calls within the context.

        :param products: User Agent products to append for red team context
        :type products: str

        ..see-also::

            `User-Agent section of RFC 9110, <https://www.rfc-editor.org/rfc/rfc9110#name-user-agent>`
        """
        default_redteam_product = "(type=redteam; subtype=RedTeam)"
        all_products = [default_redteam_product] + list(products)
        with cls.add_useragent_product(*all_products):
            yield
