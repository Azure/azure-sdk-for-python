# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import AsyncIterable, List

from ._client import DeidentificationClient as DeidentificationClientGenerated
from azure.health.deidentification.models import DocumentDetails, DeidentificationJob

__all__: List[str] = [
    "DeidentificationClient",
]  # Add all objects you want publicly available to users at this package level


class DeidentificationClient(DeidentificationClientGenerated):

    def list_jobs(self) -> AsyncIterable[DeidentificationJob]:
        """
        List de-identification jobs.

        :return: An iterator like instance of DeidentificationJob
        :rtype: ~azure.core.paging.ItemPaged[~azure.health.deidentification.models.DeidentificationJob]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._list_jobs_internal()

    def list_job_documents(self, job_name) -> AsyncIterable[DocumentDetails]:
        """
        List processed documents within a job.

        :param job_name: The name of a job. Required.
        :type job_name: str
        :return: An iterator like instance of DocumentDetails
        :rtype: ~azure.core.paging.ItemPaged[~azure.health.deidentification.models.DocumentDetails]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._list_job_documents_internal(job_name)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
