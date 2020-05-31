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

def run(cmd):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
    )
    stdout, stderr = proc.communicate()
 
    return proc.returncode, stdout, stderr

def _test_file(file_name, root_dir='.'):
    code, _, err = run([sys.executable, root_dir + '/' + file_name])
    assert code == 0
    assert err is None

def test_sample_authentication():
    _test_file('sample_authentication.py')

def test_sample_copy_model():
    _test_file('sample_copy_model.py')

def test_sample_differentiate_output_models_trained_with_and_without_labels():
    _test_file('sample_differentiate_output_models_trained_with_and_without_labels.py')

def test_sample_get_bounding_boxes():
    _test_file('sample_get_bounding_boxes.py')

def test_sample_manage_custom_models():
    _test_file('sample_manage_custom_models.py')

def test_sample_recognize_content():
    _test_file('sample_recognize_content.py')

def test_sample_recognize_custom_forms():
    _test_file('sample_recognize_custom_forms.py')

def test_sample_recognize_receipts_from_url():
    _test_file('sample_recognize_receipts_from_url.py')

def test_sample_recognize_receipts():
    _test_file('sample_recognize_receipts.py')

def test_sample_train_model_with_labels():
    _test_file('sample_train_model_with_labels.py')

def test_sample_train_model_without_labels():
    _test_file('sample_train_model_without_labels.py')


# Async sample tests

def test_sample_authentication_async():
    _test_file('sample_authentication_async.py', './async_samples')

def test_sample_copy_model_async():
    _test_file('sample_copy_model_async.py')

def test_sample_differentiate_output_models_trained_with_and_without_labels_async():
    _test_file('sample_differentiate_output_models_trained_with_and_without_labels_async.py', './async_samples')

def test_sample_get_bounding_boxes_async():
    _test_file('sample_get_bounding_boxes_async.py', './async_samples')

def test_sample_manage_custom_models_async():
    _test_file('sample_manage_custom_models_async.py', './async_samples')

def test_sample_recognize_content_async():
    _test_file('sample_recognize_content_async.py', './async_samples')

def test_sample_recognize_custom_forms_async():
    _test_file('sample_recognize_custom_forms_async.py', './async_samples')

def test_sample_recognize_receipts_from_url_async():
    _test_file('sample_recognize_receipts_from_url_async.py', './async_samples')

def test_sample_recognize_receipts_async():
    _test_file('sample_recognize_receipts_async.py', './async_samples')

def test_sample_train_model_with_labels_async():
    _test_file('sample_train_model_with_labels_async.py', './async_samples')

def test_sample_train_model_without_labels_async():
    _test_file('sample_train_model_without_labels_async.py', './async_samples')


if __name__=='__main__':
    test_sample_authentication()
    test_sample_copy_model()
    test_sample_differentiate_output_models_trained_with_and_without_labels()
    test_sample_get_bounding_boxes()
    test_sample_manage_custom_models()
    test_sample_recognize_content()
    test_sample_recognize_custom_forms()
    test_sample_recognize_receipts_from_url()
    test_sample_recognize_receipts()
    test_sample_train_model_with_labels()
    test_sample_train_model_without_labels()
    # async tests
    test_sample_authentication_async()
    test_sample_copy_model_async()
    test_sample_differentiate_output_models_trained_with_and_without_labels_async()
    test_sample_get_bounding_boxes_async()
    test_sample_manage_custom_models_async()
    test_sample_recognize_content_async()
    test_sample_recognize_custom_forms_async()
    test_sample_recognize_receipts_from_url_async()
    test_sample_recognize_receipts_async()
    test_sample_train_model_with_labels_async()
    test_sample_train_model_without_labels_async()

