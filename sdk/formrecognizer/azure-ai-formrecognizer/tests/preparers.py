
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer, get_credential, is_live

ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
REGION = os.getenv('FORMRECOGNIZER_LOCATION', None)


FormRecognizerPreparer = functools.partial(
    PowerShellPreparer,
    'formrecognizer',
    formrecognizer_test_endpoint="https://fakeendpoint.cognitiveservices.azure.com",
    formrecognizer_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_testing_data_container_sas_url="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_2="https://blob_sas_url",
    formrecognizer_selection_mark_storage_container_sas_url="https://blob_sas_url",
    formrecognizer_table_variable_rows_container_sas_url="https://blob_sas_url",
    formrecognizer_table_fixed_rows_container_sas_url="https://blob_sas_url",
    formrecognizer_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_multipage_storage_container_sas_url_2_v2="https://blob_sas_url",
    formrecognizer_selection_mark_storage_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_table_variable_rows_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_table_fixed_rows_container_sas_url_v2="https://blob_sas_url",
    formrecognizer_training_data_classifier="https://blob_sas_url",
    formrecognizer_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname/providers/Microsoft.CognitiveServices/accounts/formrecognizername",
    formrecognizer_region="region"
)


def get_async_client(client_cls, **kwargs):
    ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
    if is_live():
        form_recognizer_account = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        polling_interval = 5
    else:
        form_recognizer_account = "https://fakeendpoint.cognitiveservices.azure.com"
        polling_interval = 0
    return client_cls(
        form_recognizer_account,
        get_credential(),
        polling_interval=polling_interval,
        logging_enable=True if ENABLE_LOGGER == "True" else False,
        **kwargs
    )


def get_async_client(client_cls, **kwargs):
    ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")
    if is_live():
        form_recognizer_account = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        polling_interval = 5
    else:
        form_recognizer_account = "https://fakeendpoint.cognitiveservices.azure.com"
        polling_interval = 0
    return client_cls(
        form_recognizer_account,
        get_credential(is_async=True),
        polling_interval=polling_interval,
        logging_enable=True if ENABLE_LOGGER == "True" else False,
        **kwargs
    )
