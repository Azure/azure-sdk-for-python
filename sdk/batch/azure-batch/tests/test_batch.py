# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
import io
import hashlib
import logging
import time
import binascii
import json
import pytest
import requests
import six
import os


from wsgiref.handlers import format_date_time
from time import mktime

import azure.core.exceptions
from azure.batch import models
from azure.batch.aio import BatchClient as AsyncBatchClient
from azure.batch import BatchClient as SyncBatchClient
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar

from batch_preparers import AccountPreparer, PoolPreparer, JobPreparer

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    CachedResourceGroupPreparer,
    set_custom_default_matcher,
)
from devtools_testutils.fake_credentials import BATCH_TEST_PASSWORD
from azure_devtools.scenario_tests.recording_processors import (
    GeneralNameReplacer,
    RecordingProcessor,
)
from tests.async_wrapper import async_wrapper
from tests.proxy_decorator import recorded_by_proxy_async, client_setup

TEST_SYNC_CLIENT = True
BatchClient = SyncBatchClient if TEST_SYNC_CLIENT else AsyncBatchClient

AZURE_LOCATION = "eastasia"
BATCH_ENVIRONMENT = None  # Set this to None if testing against prod
BATCH_RESOURCE = "https://batch.core.windows.net/"
DEFAULT_VM_SIZE = "standard_d2_v2"
SECRET_FIELDS = ["primary", "secondary"]


def get_redacted_key(key):
    redacted_value = "redacted"
    digest = hashlib.sha256(six.ensure_binary(key)).digest()
    redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
    return redacted_value


class RecordingRedactor(RecordingProcessor):
    """Removes keys from test recordings"""

    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
        except (KeyError, ValueError):
            return response

        for field in body:
            if field in SECRET_FIELDS:
                body[field] = get_redacted_key(body[field])

        response["body"]["string"] = json.dumps(body)
        return response


class TestBatch(AzureMgmtRecordedTestCase):
    scrubber = GeneralNameReplacer()
    redactor = RecordingRedactor()

    def fail(self, err):
        raise RuntimeError(err)

    async def assertBatchError(self, code, func, *args, **kwargs):
        try:
            await async_wrapper(func(*args, **kwargs))
            self.fail("BatchErrorException expected but not raised")
        except azure.core.exceptions.HttpResponseError as err:
            batcherror = err.model
            # self.assertEqual(err.error.code, code)
            assert err.error.code == code
        except Exception as err:
            self.fail("Expected BatchErrorExcption, instead got: {!r}".format(err))

    async def assertCreateTasksError(self, code, func, *args, **kwargs):
        try:
            await async_wrapper(func(*args, **kwargs))
            self.fail("CreateTasksError expected but not raised")
        except models.CreateTasksErrorException as err:
            try:
                batch_error = err.errors.pop()
                if code:
                    # self.assertEqual(batch_error.error.code, code)
                    assert batch_error.error.code == code
            except IndexError:
                self.fail("Inner BatchErrorException expected but not exist")
        except Exception as err:
            self.fail("Expected CreateTasksError, instead got: {!r}".format(err))

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix="batch1", location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @JobPreparer()
    @client_setup(BatchClient)
    @recorded_by_proxy_async
    async def test_batch_applications(self, client, **kwargs):
        batch_job = kwargs.pop("batch_job")
        # Test List Applications
        apps = list(await async_wrapper(client.list_applications()))
        # apps = list(await async_wrapper(client.list_applications()))
        assert len(apps) == 1

        # Test Get Application
        app = await async_wrapper(client.get_application("application_id"))
        assert isinstance(app, models.BatchApplication)
        assert app.id == "application_id"
        assert app.versions == ["v1.0"]

        # Test Create Task with Application Package
        task_id = "python_task_with_app_package"
        task = models.BatchTaskCreateOptions(
            id=task_id,
            command_line='cmd /c "echo hello world"',
            application_package_references=[
                models.ApplicationPackageReference(
                    application_id="application_id", version="v1.0"
                )
            ],
        )
        response = await async_wrapper(client.create_task(batch_job.id, task))
        assert response is None

        # Test Get Task with Application Package
        task = await async_wrapper(client.get_task(batch_job.id, task_id))
        assert isinstance(task, models.BatchTask)
        assert task.application_package_references[0].application_id == "application_id"

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @client_setup(BatchClient)
    @recorded_by_proxy_async
    async def test_batch_certificates(self, client, **kwargs):
        # Test Add Certificate
        certificate = models.BatchCertificate(
            thumbprint="cff2ab63c8c955aaf71989efa641b906558d9fb7",
            thumbprint_algorithm="sha1",
            data="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",
            certificate_format=models.CertificateFormat.pfx,
            password="nodesdk",
        )

        response = await async_wrapper(client.create_certificate(certificate))
        assert response is None

        # Test List Certificates
        certs = await async_wrapper(client.list_certificates())
        test_cert = [
            c
            for c in certs
            if c.thumbprint == "cff2ab63c8c955aaf71989efa641b906558d9fb7"
        ]
        assert len(test_cert) == 1

        # Test Get Certificate
        cert = await async_wrapper(
            client.get_certificate("sha1", "cff2ab63c8c955aaf71989efa641b906558d9fb7")
        )
        assert isinstance(cert, models.BatchCertificate)
        assert cert.thumbprint == "cff2ab63c8c955aaf71989efa641b906558d9fb7"
        assert cert.thumbprint_algorithm == "sha1"
        assert cert.delete_certificate_error is None

        # Test Cancel Certificate Delete
        await self.assertBatchError(
            "CertificateStateActive",
            client.cancel_certificate_deletion,
            "sha1",
            "cff2ab63c8c955aaf71989efa641b906558d9fb7",
        )

        # Test Delete Certificate
        response = await async_wrapper(
            client.delete_certificate(
                "sha1", "cff2ab63c8c955aaf71989efa641b906558d9fb7"
            )
        )
        assert response is None
