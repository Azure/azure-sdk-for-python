# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Dict
from ._models_py3 import (
    AzureBlobFileListSource as GeneratedAzureBlobFileListSource,
    AzureBlobContentSource as GeneratedAzureBlobContentSource,
    ClassifierDocumentTypeDetails as GeneratedClassifierDocumentTypeDetails
)


class AzureBlobFileListSource(GeneratedAzureBlobFileListSource):
    """File list in Azure Blob Storage."""

    container_url: str
    """Required. Azure Blob Storage container URL."""
    file_list: str
    """Required. Path to a JSONL file within the container specifying a subset of
     documents for training."""

    def __init__(
        self,
        container_url: str,
        file_list: str,
        **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        super(AzureBlobFileListSource, self).__init__(container_url=container_url, file_list=file_list)
        self.container_url = container_url
        self.file_list = file_list

    def __repr__(self) -> str:
        return (
            f"AzureBlobFileListSource(container_url={self.container_url}, file_list={self.file_list})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            container_url=model.container_url,
            file_list=model.file_list
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of AzureBlobFileListSource."""
        return {
            "container_url": self.container_url,
            "file_list": self.file_list
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AzureBlobFileListSource":
        """Converts a dict in the shape of a AzureBlobFileListSource to the model itself.

        :param Dict[str, Any] data: A dictionary in the shape of AzureBlobFileListSource.
        :return: AzureBlobFileListSource
        :rtype: AzureBlobFileListSource
        """
        return cls(
            container_url=data.get("container_url", None),
            file_list=data.get("file_list", None),
        )


class AzureBlobContentSource(GeneratedAzureBlobContentSource):
    """Azure Blob Storage content."""

    container_url: str
    """Required. Azure Blob Storage container URL."""
    prefix: Optional[str]
    """Blob name prefix."""

    def __init__(
        self,
        container_url: str,
        *,
        prefix: Optional[str] = None,
        **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        super(AzureBlobContentSource, self).__init__(container_url=container_url, prefix=prefix)
        self.container_url = container_url
        self.prefix = prefix

    def __repr__(self) -> str:
        return (
            f"AzureBlobContentSource(container_url={self.container_url}, prefix={self.prefix})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            container_url=model.container_url,
            prefix=model.prefix
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of AzureBlobContentSource."""
        return {
            "container_url": self.container_url,
            "prefix": self.prefix
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AzureBlobContentSource":
        """Converts a dict in the shape of a AzureBlobContentSource to the model itself.

        :param Dict[str, Any] data: A dictionary in the shape of AzureBlobContentSource.
        :return: AzureBlobContentSource
        :rtype: AzureBlobContentSource
        """
        return cls(
            container_url=data.get("container_url", None),
            prefix=data.get("prefix", None),
        )


class ClassifierDocumentTypeDetails(GeneratedClassifierDocumentTypeDetails):
    """Training data source. Pass either `azure_blob_source` or `azure_blob_file_list_source`."""

    azure_blob_source: Optional[AzureBlobContentSource]
    """Azure Blob Storage location containing the training data."""
    azure_blob_file_list_source: Optional[AzureBlobFileListSource]
    """Azure Blob Storage file list specifying the training data."""

    def __init__(
        self,
        *,
        azure_blob_source: Optional[AzureBlobContentSource] = None,
        azure_blob_file_list_source: Optional[AzureBlobFileListSource] = None,
        **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        super(ClassifierDocumentTypeDetails, self).__init__(
            azure_blob_source=azure_blob_source,
            azure_blob_file_list_source=azure_blob_file_list_source
        )
        self.azure_blob_source = azure_blob_source
        self.azure_blob_file_list_source = azure_blob_file_list_source

    def __repr__(self) -> str:
        return (
            f"ClassifierDocumentTypeDetails(azure_blob_source={self.azure_blob_source}, "
            f"azure_blob_file_list_source={self.azure_blob_file_list_source})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            azure_blob_source=AzureBlobContentSource._from_generated(model.azure_blob_source)
            if model.azure_blob_source is not None else None,
            azure_blob_file_list_source=AzureBlobFileListSource._from_generated(model.azure_blob_file_list_source)
            if model.azure_blob_file_list_source is not None else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of ClassifierDocumentTypeDetails."""
        return {
            "azure_blob_source": self.azure_blob_source.to_dict() if self.azure_blob_source else None,
            "azure_blob_file_list_source": self.azure_blob_file_list_source.to_dict()
            if self.azure_blob_file_list_source else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClassifierDocumentTypeDetails":
        """Converts a dict in the shape of a ClassifierDocumentTypeDetails to the model itself.

        :param Dict[str, Any] data: A dictionary in the shape of ClassifierDocumentTypeDetails.
        :return: ClassifierDocumentTypeDetails
        :rtype: ClassifierDocumentTypeDetails
        """
        return cls(
            azure_blob_source=AzureBlobContentSource.from_dict(data.get("azure_blob_source"))  # type: ignore
            if data.get("azure_blob_source") else None,
            azure_blob_file_list_source=AzureBlobFileListSource.from_dict(data.get("azure_blob_file_list_source"))  # type: ignore
            if data.get("azure_blob_file_list_source") else None
        )


__all__: List[str] = ["AzureBlobFileListSource", "AzureBlobContentSource", "ClassifierDocumentTypeDetails"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
