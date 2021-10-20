# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from time import sleep
import pytest
from azure.iot.modelsrepository._metadata_scheduler import (
    MetadataScheduler
)

@pytest.mark.describe("MetadataScheduler")
class MetadataSchedulerTests(object):
    @pytest.mark.it("MetadataScheduler with expiration time of one second.")
    def test_basic_usage(self):
        scheduler = MetadataScheduler(1)
        # initial fetch should return true
        assert scheduler.has_elapsed()
        assert scheduler.has_elapsed()
        assert scheduler.reset()
        assert not scheduler.has_elapsed()
        sleep(2)
        assert scheduler.has_elapsed()

    @pytest.mark.it("MetadataScheduler with expiration time of zero seconds.")
    def test_continuous_elapse(self):
        scheduler = MetadataScheduler(0)
        # initial fetch should return true
        assert scheduler.has_elapsed()
        assert scheduler.has_elapsed()
        assert scheduler.reset()
        assert scheduler.has_elapsed()
        assert scheduler.reset()
        assert scheduler.has_elapsed()

    @pytest.mark.it("MetadataScheduler with default expiration time of infinite seconds.")
    def test_basic_usage(self):
        scheduler = MetadataScheduler()
        # initial fetch should return true
        assert scheduler.has_elapsed()
        assert scheduler.has_elapsed()
        assert scheduler.reset()
        assert not scheduler.has_elapsed()
        assert scheduler.reset()
        assert not scheduler.has_elapsed()

    @pytest.mark.it("MetadataScheduler disabled.")
    def test_basic_usage(self):
        scheduler = MetadataScheduler(enabled=False)
        assert not scheduler.has_elapsed()
        assert not scheduler.has_elapsed()
        assert scheduler.reset()
        assert not scheduler.has_elapsed()
        assert scheduler.reset()
        assert not scheduler.has_elapsed()
