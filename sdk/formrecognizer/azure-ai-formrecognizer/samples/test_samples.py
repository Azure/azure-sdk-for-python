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

for file_name in os.listdir('.'):
    if file_name.startswith('sample_'):
        code, _, err = run([sys.executable, file_name])
        print(file_name)
        assert code == 0
        assert err is None

for file_name in os.listdir('./async_samples'):
    if file_name.startswith('async_samples/' + 'sample_'):
        code, _, err = run([sys.executable, file_name])
        print(file_name)
        assert code == 0
        assert err is None
