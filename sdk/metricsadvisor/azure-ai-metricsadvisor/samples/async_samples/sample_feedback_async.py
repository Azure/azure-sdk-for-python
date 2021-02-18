# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_feedback_async.py
DESCRIPTION:
    This sample demonstrates feedback operations.
USAGE:
    python sample_feedback_async.py

    Set the environment variables with your own values before running the sample:
    1) METRICS_ADVISOR_ENDPOINT - the endpoint of your Azure Metrics Advisor service
    2) METRICS_ADVISOR_SUBSCRIPTION_KEY - Metrics Advisor service subscription key
    3) METRICS_ADVISOR_API_KEY - Metrics Advisor service API key
    4) METRICS_ADVISOR_METRIC_ID - the ID of an metric from an existing data feed
    5) METRICS_ADVISOR_FEEDBACK_ID - the ID of an existing feedback
"""

import os
import datetime
import asyncio


async def sample_add_feedback_async():
    # [START add_feedback_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient
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
    await client.add_feedback(anomaly_feedback)

    change_point_feedback = ChangePointFeedback(metric_id=metric_id,
                                                dimension_key={"Dim1": "Common Lime"},
                                                start_time=datetime.datetime(2020, 8, 5),
                                                end_time=datetime.datetime(2020, 8, 7),
                                                value="NotChangePoint")
    await client.add_feedback(change_point_feedback)

    comment_feedback = CommentFeedback(metric_id=metric_id,
                                       dimension_key={"Dim1": "Common Lime"},
                                       start_time=datetime.datetime(2020, 8, 5),
                                       end_time=datetime.datetime(2020, 8, 7),
                                       value="comment")
    await client.add_feedback(comment_feedback)

    period_feedback = PeriodFeedback(metric_id=metric_id,
                                     dimension_key={"Dim1": "Common Lime"},
                                     start_time=datetime.datetime(2020, 8, 5),
                                     end_time=datetime.datetime(2020, 8, 7),
                                     period_type="AssignValue",
                                     value=2)
    await client.add_feedback(period_feedback)
    # [END add_feedback_async]


async def sample_get_feedback_async():
    # [START get_feedback_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    feedback_id = os.getenv("METRICS_ADVISOR_FEEDBACK_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    result = await client.get_feedback(feedback_id=feedback_id)
    print("Type: {}; Id: {}".format(result.feedback_type, result.id))
    # [END get_feedback_async]


async def sample_list_feedback_async():
    # [START list_feedback_async]
    from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
    from azure.ai.metricsadvisor.aio import MetricsAdvisorClient

    service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT")
    subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY")
    api_key = os.getenv("METRICS_ADVISOR_API_KEY")
    metric_id = os.getenv("METRICS_ADVISOR_METRIC_ID")

    client = MetricsAdvisorClient(service_endpoint,
                                  MetricsAdvisorKeyCredential(subscription_key, api_key))

    results = client.list_feedback(metric_id=metric_id)
    async for result in results:
        print("Type: {}; Id: {}".format(result.feedback_type, result.id))
    # [END list_feedback_async]

async def main():
    print("---Creating feedback...")
    await sample_add_feedback_async()
    print("Feedback successfully created...")
    print("\n---Get a feedback...")
    await sample_get_feedback_async()
    print("\n---List feedbacks...")
    await sample_list_feedback_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
