import asyncio
import functools
import inspect
import os
import random
import datetime
import uuid
from typing import List, Optional

from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncLROPoller, LROPoller
from azure.core.polling.base_polling import OperationFailed
from azure.health.deidentification import DeidentificationClient
from azure.health.deidentification.aio import (
    DeidentificationClient as DeidentificationClientAsync,
)
from azure.health.deidentification.models import (
    DeidentificationDocumentDetails,
    DeidentificationJob,
    OperationStatus,
)


from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

RealtimeEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="https://example-deid.api.deid.azure.com",
)

BatchEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="https://example-deid.api.deid.azure.com",
    healthdataaiservices_storage_account_name="blobstorageaccount",
    healthdataaiservices_storage_container_name="containername",
)


JOB_TIMEOUT_SECONDS = 600
MAX_DIAGNOSTIC_DOCUMENTS = 20


def format_job_diagnostics(job: DeidentificationJob, documents: List[DeidentificationDocumentDetails]) -> str:
    lines = [
        f"Job '{job.job_name}' status: {job.status}",
        f"  created_at={job.created_at} started_at={job.started_at} last_updated_at={job.last_updated_at}",
    ]
    if job.summary is not None:
        s = job.summary
        lines.append(
            f"  summary: total={s.total_count} successful={s.successful_count} "
            f"failed={s.failed_count} canceled={s.canceled_count} bytes_processed={s.bytes_processed}"
        )
    else:
        lines.append("  summary: None")
    lines.append(f"  error: {job.error if job.error is not None else 'None'}")
    if documents:
        lines.append(f"  unsuccessful documents (up to {MAX_DIAGNOSTIC_DOCUMENTS}):")
        for doc in documents:
            location = doc.input_location.location if doc.input_location is not None else doc.id
            lines.append(f"    - {location} status={doc.status} error={doc.error}")
    return "\n".join(lines)


def _is_unsuccessful(doc: DeidentificationDocumentDetails) -> bool:
    return doc.status != OperationStatus.SUCCEEDED or doc.error is not None


class DeidBaseTestCase(AzureRecordedTestCase):
    OUTPUT_PATH = "_output"

    def describe_job(self, client: DeidentificationClient, job_name: str) -> str:
        """Fetch the job and its unsuccessful documents and format them for an assertion message."""
        try:
            job = client.get_job(job_name)
            documents: List[DeidentificationDocumentDetails] = []
            for doc in client.list_job_documents(job_name):
                if _is_unsuccessful(doc):
                    documents.append(doc)
                    if len(documents) >= MAX_DIAGNOSTIC_DOCUMENTS:
                        break
            return format_job_diagnostics(job, documents)
        except Exception as e:  # pylint: disable=broad-except
            # Diagnostics must never mask the original failure.
            return f"Unable to fetch diagnostics for job '{job_name}': {e!r}"

    async def describe_job_async(self, client: DeidentificationClientAsync, job_name: str) -> str:
        """Async version of describe_job."""
        try:
            job = await client.get_job(job_name)
            documents: List[DeidentificationDocumentDetails] = []
            async for doc in client.list_job_documents(job_name):
                if _is_unsuccessful(doc):
                    documents.append(doc)
                    if len(documents) >= MAX_DIAGNOSTIC_DOCUMENTS:
                        break
            return format_job_diagnostics(job, documents)
        except Exception as e:  # pylint: disable=broad-except
            return f"Unable to fetch diagnostics for job '{job_name}': {e!r}"

    def wait_for_job(
        self,
        client: DeidentificationClient,
        poller: LROPoller[DeidentificationJob],
        job_name: str,
        timeout: Optional[float] = JOB_TIMEOUT_SECONDS,
    ) -> DeidentificationJob:
        """Wait for a job LRO and fail with the job's real error instead of azure-core's generic polling error.

        azure-core surfaces a Failed/Canceled job as HttpResponseError("Operation returned an invalid status 'OK'"),
        and LROPoller.result(timeout) silently returns the in-progress job when the timeout expires.
        """
        try:
            job = poller.result(timeout=timeout)
        except (HttpResponseError, OperationFailed) as e:
            raise AssertionError(
                f"Job '{job_name}' did not succeed ({e}).\n{self.describe_job(client, job_name)}"
            ) from e
        if not poller.done():
            raise AssertionError(
                f"Job '{job_name}' did not reach a terminal state within {timeout}s.\n"
                f"{self.describe_job(client, job_name)}"
            )
        return job

    async def wait_for_job_async(
        self,
        client: DeidentificationClientAsync,
        poller: AsyncLROPoller[DeidentificationJob],
        job_name: str,
        timeout: Optional[float] = JOB_TIMEOUT_SECONDS,
    ) -> DeidentificationJob:
        """Async version of wait_for_job."""
        try:
            return await asyncio.wait_for(poller.result(), timeout=timeout)
        except asyncio.TimeoutError as e:
            raise AssertionError(
                f"Job '{job_name}' did not reach a terminal state within {timeout}s.\n"
                f"{await self.describe_job_async(client, job_name)}"
            ) from e
        except (HttpResponseError, OperationFailed) as e:
            raise AssertionError(
                f"Job '{job_name}' did not succeed ({e}).\n{await self.describe_job_async(client, job_name)}"
            ) from e

    def make_client(self, endpoint) -> DeidentificationClient:
        credential = self.get_credential(DeidentificationClient)
        connection_verify = not "localhost" in endpoint
        client = self.create_client_from_credential(
            DeidentificationClient, credential=credential, endpoint=endpoint, connection_verify=connection_verify
        )
        return client

    def make_client_async(self, endpoint) -> DeidentificationClientAsync:
        credential = self.get_credential(DeidentificationClientAsync)
        client = self.create_client_from_credential(
            DeidentificationClientAsync,
            credential=credential,
            endpoint=endpoint,
            connection_verify=False,  # If not set, the test proxy overwrites the endpoint to localhost:5001
        )
        return client

    def generate_job_name(self) -> str:
        caller_function_name = inspect.stack()[1].function
        uniquifier = os.environ.get("HEALTHDATAAISERVICES_UNIQUIFIER", "")
        job_name = f"{caller_function_name[:28]}-{uniquifier}"
        return job_name

    def get_storage_location(self, kwargs):
        storage_name: str = kwargs.pop("healthdataaiservices_storage_account_name")
        container_name: str = kwargs.pop("healthdataaiservices_storage_container_name")
        storage_location = f"https://{storage_name}.blob.core.windows.net/{container_name}"
        sas_uri = os.environ.get("HEALTHDATAAISERVICES_SAS_URI", "")
        if (
            os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() == "true"  # Don't override uniquifier by default
            and os.environ.get("AZURE_SKIP_LIVE_RECORDING", "false").lower() != "true"
        ):
            if sas_uri != "" and os.environ:
                print(f"Using SAS URI: {sas_uri}")
                return sas_uri

        print(f"Using storage location: {storage_location}")
        return storage_location
