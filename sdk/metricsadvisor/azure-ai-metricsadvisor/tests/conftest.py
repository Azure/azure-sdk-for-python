# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys
import os
import pytest
from devtools_testutils import (
    test_proxy,
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer
)

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT", "https://fakeendpoint.cognitiveservices.azure.com")
    service_endpoint = service_endpoint.rstrip("/")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY", "metrics_advisor_subscription_key")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY", "metrics_advisor_api_key")
    metrics_advisor_sql_server_connection_string = os.getenv("METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING", "metrics_advisor_sql_server_connection_string")
    metrics_advisor_anomaly_detection_configuration_id = os.getenv("METRICS_ADVISOR_ANOMALY_DETECTION_CONFIGURATION_ID", "metrics_advisor_anomaly_detection_configuration_id")
    metrics_advisor_data_feed_id = os.getenv("METRICS_ADVISOR_DATA_FEED_ID", "metrics_advisor_data_feed_id")
    metrics_advisor_metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID", "metrics_advisor_metric_id")
    metrics_advisor_anomaly_alert_configuration_id = os.getenv("METRICS_ADVISOR_ANOMALY_ALERT_CONFIGURATION_ID", "metrics_advisor_anomaly_alert_configuration_id")
    metrics_advisor_incident_id = os.getenv("METRICS_ADVISOR_INCIDENT_ID", "metrics_advisor_incident_id")
    metrics_advisor_feedback_id = os.getenv("METRICS_ADVISOR_FEEDBACK_ID", "metrics_advisor_feedback_id")
    metrics_advisor_alert_id = os.getenv("METRICS_ADVISOR_ALERT_ID", "metrics_advisor_alert_id")

    add_general_regex_sanitizer(regex=service_endpoint, value="https://fakeendpoint.cognitiveservices.azure.com")
    add_general_regex_sanitizer(regex=subscription_key, value="metrics_advisor_subscription_key")
    add_general_regex_sanitizer(regex=api_key, value="metrics_advisor_api_key")
    add_general_regex_sanitizer(regex=metrics_advisor_sql_server_connection_string, value="metrics_advisor_sql_server_connection_string")
    add_general_regex_sanitizer(regex=metrics_advisor_anomaly_detection_configuration_id, value="metrics_advisor_anomaly_detection_configuration_id")
    add_general_regex_sanitizer(regex=metrics_advisor_data_feed_id, value="metrics_advisor_data_feed_id")
    add_general_regex_sanitizer(regex=metrics_advisor_metric_id, value="metrics_advisor_metric_id")
    add_general_regex_sanitizer(regex=metrics_advisor_anomaly_alert_configuration_id, value="metrics_advisor_anomaly_alert_configuration_id")
    add_general_regex_sanitizer(regex=metrics_advisor_incident_id, value="metrics_advisor_incident_id")
    add_general_regex_sanitizer(regex=metrics_advisor_feedback_id, value="metrics_advisor_feedback_id")
    add_general_regex_sanitizer(regex=metrics_advisor_alert_id, value="metrics_advisor_alert_id")
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")
    add_remove_header_sanitizer(headers="x-api-key")
    add_oauth_response_sanitizer()
