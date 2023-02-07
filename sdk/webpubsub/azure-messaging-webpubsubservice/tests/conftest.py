# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

def pytest_sessionfinish(session, exitstatus):
    # We get status 5 when no tests are collected -- this raises as a failure in CI
    if exitstatus == 5:
        session.exitstatus = 0  # Flag the run as successful because we expect this outcome
