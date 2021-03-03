#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import datetime as dt
from datetime import timedelta
from msrest.serialization import UTC

from azure.eventgrid import generate_sas

def test_generate_sas_fails_with_http():
    expiration_date_utc = dt.datetime.now(UTC()) + timedelta(hours=1)
    http_endpoint = "http://topic.eventgrid.endpoint"
    with pytest.raises(ValueError):
        signature = generate_sas(http_endpoint, "eventgrid_topic_primary_key", expiration_date_utc)

def test_generate_sas_adds_https_if_not_exists():
    expiration_date_utc = dt.datetime.now(UTC()) + timedelta(hours=1)
    http_endpoint = "topic.eventgrid.endpoint"
    signature = generate_sas(http_endpoint, "eventgrid_topic_primary_key", expiration_date_utc)
    assert signature.startswith("r=https")

def test_generate_sas_adds_https_appends_api_events():
    expiration_date_utc = dt.datetime.now(UTC()) + timedelta(hours=1)
    http_endpoint = "https://topic.eventgrid.endpoint"
    signature = generate_sas(http_endpoint, "eventgrid_topic_primary_key", expiration_date_utc)
    assert "%2Fapi%2Fevents" in signature