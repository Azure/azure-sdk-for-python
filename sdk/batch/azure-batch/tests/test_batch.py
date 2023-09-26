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
from async_wrapper import async_wrapper
from proxy_decorator import recorded_by_proxy_async


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

    def _batch_url(self, batch):
        if batch.account_endpoint.startswith("https://"):
            return batch.account_endpoint
        else:
            return "https://" + batch.account_endpoint

    def create_aad_client(self, batch_account, **kwargs):
        credential = self.settings.get_credentials(resource=BATCH_RESOURCE)
        client = self.create_basic_client(
            BatchClient, credential=credential, endpoint=self._batch_url(batch_account)
        )
        return client

    def create_sharedkey_client(self, batch_account, credential, **kwargs):
        client = BatchClient(
            credential=credential, endpoint=self._batch_url(batch_account)
        )
        return client

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
    @recorded_by_proxy_async
    async def test_batch_applications(self, **kwargs):
        batch_job = kwargs.pop("batch_job")
        client = self.create_sharedkey_client(**kwargs)
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

