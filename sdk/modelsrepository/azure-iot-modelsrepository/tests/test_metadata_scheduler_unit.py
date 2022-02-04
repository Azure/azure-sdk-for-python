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
    @pytest.mark.it("Enabled MetadataScheduler should support only an initial metadata fetch.")
    def test_metadata_scheduler_enabled(self):
        scheduler = MetadataScheduler()
        # initial fetch should return true
        assert scheduler.should_fetch_metadata()
        assert scheduler.should_fetch_metadata()
        assert scheduler.mark_as_fetched()
        assert not scheduler.should_fetch_metadata()
        assert scheduler.mark_as_fetched()
        assert not scheduler.should_fetch_metadata()

    @pytest.mark.it("Disabled MetadataScheduler should support no metadata fetching.")
    def test_metadata_scheduler_disabled(self):
        scheduler = MetadataScheduler(enabled=False)
        assert not scheduler.should_fetch_metadata()
        assert not scheduler.should_fetch_metadata()
        assert scheduler.mark_as_fetched()
        assert not scheduler.should_fetch_metadata()
        assert scheduler.mark_as_fetched()
        assert not scheduler.should_fetch_metadata()
