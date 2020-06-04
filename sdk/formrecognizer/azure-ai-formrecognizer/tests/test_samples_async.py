# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
USAGE:
    python test_samples.py

    Set the environment variables with your own values before running the samples.
    See independent sample files to check what env variables must be set.
"""


import subprocess
import sys
import os
import pytest

def run(cmd):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
    )
    stdout, stderr = proc.communicate()
 
    return proc.returncode, stdout, stderr

def _test_file(file_name, root_dir='./samples/async_samples'):
    code, _, err = run([sys.executable, root_dir + '/' + file_name])
    assert code == 0
    assert err is None

# Async sample tests
@pytest.mark.live_test_only
def test_sample_authentication_async():
    _test_file('sample_authentication_async.py')

@pytest.mark.live_test_only
def test_sample_get_bounding_boxes_async():
    _test_file('sample_get_bounding_boxes_async.py')

@pytest.mark.live_test_only
def test_sample_manage_custom_models_async():
    _test_file('sample_manage_custom_models_async.py')

@pytest.mark.live_test_only
def test_sample_recognize_content_async():
    _test_file('sample_recognize_content_async.py')

@pytest.mark.live_test_only
def test_sample_recognize_custom_forms_async():
    _test_file('sample_recognize_custom_forms_async.py')

@pytest.mark.live_test_only
def test_sample_recognize_receipts_from_url_async():
    _test_file('sample_recognize_receipts_from_url_async.py')

@pytest.mark.live_test_only
def test_sample_recognize_receipts_async():
    _test_file('sample_recognize_receipts_async.py')

@pytest.mark.live_test_only
def test_sample_train_model_with_labels_async():
    _test_file('sample_train_model_with_labels_async.py')

@pytest.mark.live_test_only
def test_sample_train_model_without_labels_async():
    _test_file('sample_train_model_without_labels_async.py')


if __name__=='__main__':
    # async tests
    test_sample_authentication_async()
    test_sample_get_bounding_boxes_async()
    test_sample_manage_custom_models_async()
    test_sample_recognize_content_async()
    test_sample_recognize_custom_forms_async()
    test_sample_recognize_receipts_from_url_async()
    test_sample_recognize_receipts_async()
    test_sample_train_model_with_labels_async()
    test_sample_train_model_without_labels_async()
