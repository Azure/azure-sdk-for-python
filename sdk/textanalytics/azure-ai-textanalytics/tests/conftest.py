
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest
from devtools_testutils import add_remove_header_sanitizer, add_general_regex_sanitizer, add_body_key_sanitizer


# Ignore async tests for Python < 3.6
collect_ignore_glob = []
if sys.version_info < (3, 6):
    collect_ignore_glob.append("*_async.py")


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers():
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")
    add_general_regex_sanitizer(
        value="fakeendpoint",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.cognitiveservices\\.azure\\.com)"
    )
    add_body_key_sanitizer(
        json_path="tasks['customSingleClassificationTasks'][*]['parameters']['project-name']",
        value="single_category_classify_project_name"
    )
    add_body_key_sanitizer(
        json_path="tasks['customSingleClassificationTasks'][*]['parameters']['deployment-name']",
        value="single_category_classify_deployment_name"
    )
    add_body_key_sanitizer(
        json_path="tasks['customMultiClassificationTasks'][*]['parameters']['project-name']",
        value="multi_category_classify_project_name"
    )
    add_body_key_sanitizer(
        json_path="tasks['customMultiClassificationTasks'][*]['parameters']['deployment-name']",
        value="multi_category_classify_deployment_name"
    )
    add_body_key_sanitizer(
        json_path="tasks['customEntityRecognitionTasks'][*]['parameters']['project-name']",
        value="custom_entities_project_name"
    )
    add_body_key_sanitizer(
        json_path="tasks['customEntityRecognitionTasks'][*]['parameters']['deployment-name']",
        value="custom_entities_deployment_name"
    )
