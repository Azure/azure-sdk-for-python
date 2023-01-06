# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_base.py

DESCRIPTION:
    This is the base class for sync samples. It imports some images that could be used in samples.
"""
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry._helpers import _import_image, _get_authority,_get_audience, _get_credential

class SampleBase(object):
    def __init__(self, is_async=False):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        self.repos = [
            "library/hello-world",
            "library/alpine",
            "library/busybox",
        ]
        self.tags = [
            [
                "library/hello-world:latest",
                "library/hello-world:v1",
                "library/hello-world:v2",
                "library/hello-world:v3",
                "library/hello-world:v4",
            ],
            ["library/alpine"],
            ["library/busybox"],
        ]
        self.authority = _get_authority(self.endpoint)
        self.audience = _get_audience(self.authority)
        self.credential = _get_credential(self.authority, exclude_environment_credential=True, is_async=is_async)

    def _set_up(self):
        self.authority = _get_authority(self.endpoint)
        print("-----------Start importing images-------------")
        for repo, tag in zip(self.repos, self.tags):
            try:
                _import_image(self.authority, repo, tag)
            except Exception as e:
                print(e)
        print("-----------Done!-------------")
