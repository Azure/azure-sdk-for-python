# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_feedback.py
DESCRIPTION:
    This sample demonstrates feedback operations.
USAGE:
    python sample_feedback.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_METRIC_ID - the ID of an metric from an existing data feed
    5) METRICS_ADVISOR_FEEDBACK_ID - the ID of an existing feedback
"""

import os
import datetime


def sample_add_feedback():
    # [START add_feedback]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient
    from azure.ai.metricsadvisor.models import AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    anomaly_feedback = AnomalyFeedback(metric_id=metric_id,
                                       dimension_key={"Dim1": "Common Lime"},
                                       start_time=datetime.datetime(2020, 8, 5),
                                       end_time=datetime.datetime(2020, 8, 7),
                                       value="NotAnomaly")
    client.add_feedback(anomaly_feedback)

    change_point_feedback = ChangePointFeedback(metric_id=metric_id,
                                                dimension_key={"Dim1": "Common Lime"},
                                                start_time=datetime.datetime(2020, 8, 5),
                                                end_time=datetime.datetime(2020, 8, 7),
                                                value="NotChangePoint")
    client.add_feedback(change_point_feedback)

    comment_feedback = CommentFeedback(metric_id=metric_id,
                                       dimension_key={"Dim1": "Common Lime"},
                                       start_time=datetime.datetime(2020, 8, 5),
                                       end_time=datetime.datetime(2020, 8, 7),
                                       value="comment")
    client.add_feedback(comment_feedback)

    period_feedback = PeriodFeedback(metric_id=metric_id,
                                     dimension_key={"Dim1": "Common Lime"},
                                     start_time=datetime.datetime(2020, 8, 5),
                                     end_time=datetime.datetime(2020, 8, 7),
                                     period_type="AssignValue",
                                     value=2)
    client.add_feedback(period_feedback)
    # [END add_feedback]


def sample_get_feedback():
    # [START get_feedback]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    feedback_id = os.getenv("METRICS_ADVISOR_FEEDBACK_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    result = client.get_feedback(feedback_id=feedback_id)
    print("Type: {}; Id: {}".format(result.feedback_type, result.id))
    # [END get_feedback]


def sample_list_feedback():
    # [START list_feedback]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential, MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_feedback(metric_id=metric_id)
    for result in results:
        print("Type: {}; Id: {}".format(result.feedback_type, result.id))
    # [END list_feedback]


if __name__ == '__main__':
    print("---Creating feedback...")
    sample_add_feedback()
    print("Feedback successfully created...")
    print("\n---Get a feedback...")
    sample_get_feedback()
    print("\n---List feedbacks...")
    sample_list_feedback()
