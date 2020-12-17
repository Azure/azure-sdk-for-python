#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


RUN_BREAKING_CHANGES_PACKAGES = [
    "azure-ai-formrecognizer",
    "azure-storage-queue"
]



IGNORE_BREAKING_CHANGES = {
    "azure-ai-formrecognizer": [
        ("RemoveOrRenameClientMethod", "azure-ai-formrecognizer.aio", "FormTrainingClient", "begin_training")
    ]
}