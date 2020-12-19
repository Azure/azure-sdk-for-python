#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


RUN_BREAKING_CHANGES_PACKAGES = [
    "azure-ai-formrecognizer",
    "azure-storage-queue",
    "azure-storage-blob",
    "azure-storage-file-share",
    "azure-keyvault-keys",
    "azure-keyvault-certificates",
    "azure-keyvault-secrets",
    "azure-storage-file-datalake",
    "azure-appconfiguration",
    "azure-core",
    "azure-eventhub",
    "azure-identity",
    "azure-search-documents",
    "azure-ai-textanalytics"
]



IGNORE_BREAKING_CHANGES = {
    "azure-ai-formrecognizer": [
        ("RemovedOrRenamedClientMethod", "azure-ai-formrecognizer.aio", "FormTrainingClient", "begin_training")
    ]
}