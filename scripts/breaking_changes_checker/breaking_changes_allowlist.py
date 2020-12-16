#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Add an ignore:
(<breaking-change-type>, <module-name>, <class-name>, <function-name>)

"azure-ai-formrecognizer": [
    ("RemoveOrRenameClientMethod", "azure.ai.formrecognizer.aio", "FormTrainingClient", "begin_training"),
    ("RemoveOrRenameModel", "azure.ai.formrecognizer", "FormElement"),
],
"azure-storage-queue": [
    ("RemoveOrRenameModuleLevelFunction", "azure.storage.queue", "generate_queue_sas")
]
"""


RUN_BREAKING_CHANGES_PACKAGES = [
    "azure-ai-formrecognizer",
    "azure-storage-queue"
]


IGNORE_BREAKING_CHANGES = {
    "azure-ai-formrecognizer": [
        ("RemoveOrRenameClientMethod", "azure-ai-formrecognizer.aio", "FormTrainingClient", "begin_training")
    ]
}