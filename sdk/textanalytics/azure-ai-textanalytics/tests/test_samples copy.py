# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import sys
import pytest
import functools
from glob import glob
from subprocess import check_call
from testcase import TextAnalyticsTest


samples_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")


@pytest.fixture(params=[pytest.param(os.path.join(samples_directory, x), id=os.path.basename(x)) for x in glob("%s/*.py" % samples_directory)])
def sample_file(request):
    return request.param


def test_sample(sample_file):
    python_cmd = [sys.executable, sample_file]
    check_call(
        python_cmd,
        env={
            "AZURE_TEXT_ANALYTICS_ENDPOINT": TextAnalyticsTest._TEXT_ANALYTICS_ACCOUNT,
            "AZURE_TEXT_ANALYTICS_KEY": TextAnalyticsTest._TEXT_ANALYTICS_KEY
        }
    )
