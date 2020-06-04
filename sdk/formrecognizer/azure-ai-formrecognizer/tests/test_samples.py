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

def _test_file(file_name, root_dir='./samples'):
    code, out, err = run([sys.executable, root_dir + '/' + file_name])
    assert code == 0
    print(out)
    assert err is None

@pytest.mark.live_test_only
def test_sample_authentication():
    _test_file('sample_authentication.py')

@pytest.mark.live_test_only
def test_sample_get_bounding_boxes():
    _test_file('sample_get_bounding_boxes.py')

@pytest.mark.live_test_only
def test_sample_manage_custom_models():
    _test_file('sample_manage_custom_models.py')

@pytest.mark.live_test_only
def test_sample_recognize_content():
    _test_file('sample_recognize_content.py')

@pytest.mark.live_test_only
def test_sample_recognize_custom_forms():
    _test_file('sample_recognize_custom_forms.py')

@pytest.mark.live_test_only
def test_sample_recognize_receipts_from_url():
    _test_file('sample_recognize_receipts_from_url.py')

@pytest.mark.live_test_only
def test_sample_recognize_receipts():
    _test_file('sample_recognize_receipts.py')

@pytest.mark.live_test_only
def test_sample_train_model_with_labels():
    _test_file('sample_train_model_with_labels.py')

@pytest.mark.live_test_only
def test_sample_train_model_without_labels():
    _test_file('sample_train_model_without_labels.py')


if __name__=='__main__':
    test_sample_authentication()
    test_sample_get_bounding_boxes()
    test_sample_manage_custom_models()
    test_sample_recognize_content()
    test_sample_recognize_custom_forms()
    test_sample_recognize_receipts_from_url()
    test_sample_recognize_receipts()
    test_sample_train_model_with_labels()
    test_sample_train_model_without_labels()
