# This class has been copied from 'langchain/langchain/schema.py
# Last Sync: 2023-09-05
# Tag: v0.0.220
from abc import ABC, abstractmethod
from typing import (
    List,
)

from azure.ai.resources._index._langchain.vendor.schema.document import Document


class BaseRetriever(ABC):
    """Base interface for retrievers."""

    @abstractmethod
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """

    @abstractmethod
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """
