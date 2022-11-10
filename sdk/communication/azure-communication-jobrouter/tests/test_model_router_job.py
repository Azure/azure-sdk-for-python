# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from datetime import datetime
from azure.core.serialization import _datetime_as_isostr  # pylint:disable=protected-access
from azure.communication.jobrouter import RouterJob


class TestRouterJob(object):

    def test_job_router_accepts_notes_with_datetime_and_str(self):

        current_timestamp = datetime.utcnow()
        current_timestamp_as_str = _datetime_as_isostr(current_timestamp)
        second_timestamp = "2022-05-13T16:59:04.531199Z"

        notes = {
            second_timestamp: "Fake notes 1",
            current_timestamp: "Fake notes 2"
        }

        router_job: RouterJob = RouterJob(
            notes = notes
        )

        assert (second_timestamp in router_job.notes) is True
        assert (current_timestamp_as_str in router_job.notes) is True

        assert router_job is not None


if __name__ == '__main__':
    unittest.main()
