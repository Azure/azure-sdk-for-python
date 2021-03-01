#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import argparse
import sys
import os
import logging
from fnmatch import fnmatch
from common_tasks import (
    run_check_call,
    process_glob_string,
)

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

IGNORED_SAMPLES = {
    "azure-eventgrid": [
        "__init__.py",
        "consume_cloud_events_from_eventhub.py",
        "consume_eventgrid_events_from_service_bus_queue.py",
        "consume_cloud_events_from_storage_queue.py",
        "sample_publish_events_to_a_topic_using_sas_credential.py",
        "sample_publish_events_to_a_topic_using_sas_credential_async.py"],
    "azure-eventhub": [
        "authenticate_with_sas_token.py",
        "connection_to_custom_endpoint_address.py",
        "proxy.py",
        "receive_batch_with_checkpoint.py",
        "recv.py",
        "recv_track_last_enqueued_event_prop.py",
        "recv_with_checkpoint_by_event_count.py",
        "recv_with_checkpoint_by_time_interval.py",
        "recv_with_checkpoint_store.py",
        "recv_with_custom_starting_position.py",
        "sample_code_eventhub.py",
        "authenticate_with_sas_token_async.py",
        "connection_to_custom_endpoint_address_async.py",
        "iot_hub_connection_string_receive_async.py",
        "proxy_async.py",
        "receive_batch_with_checkpoint_async.py",
        "recv_async.py",
        "recv_track_last_enqueued_event_prop_async.py",
        "recv_with_checkpoint_by_event_count_async.py",
        "recv_with_checkpoint_by_time_interval_async.py",
        "recv_with_checkpoint_store_async.py",
        "recv_with_custom_starting_position_async.py",
        "sample_code_eventhub_async.py"
    ],
    "azure-eventhub-checkpointstoreblob": [
        "receive_events_using_checkpoint_store.py",
        "receive_events_using_checkpoint_store_storage_api_version.py"
    ],
    "azure-eventhub-checkpointstoreblob-aio": [
        "receive_events_using_checkpoint_store_async.py",
        "receive_events_using_checkpoint_store_storage_api_version_async.py"
    ],
    "azure-servicebus": [
        "failure_and_recovery.py",
        "mgmt_queue.py",
        "mgmt_rule.py",
        "mgmt_subscription.py",
        "mgmt_topic.py",
        "proxy.py",
        "receive_deferred_message_queue.py",
        "receive_iterator_queue.py",
        "session_pool_receive.py",
        "mgmt_queue_async.py",
        "mgmt_rule_async.py",
        "mgmt_subscription_async.py",
        "mgmt_topic_async.py",
        "proxy_async.py",
        "receive_deferred_message_queue_async.py",
        "receive_iterator_queue_async.py",
        "session_pool_receive_async.py"
    ]
}


def run_samples(targeted_package):
    logging.info("running samples for {}".format(targeted_package))

    samples_errors = []
    sample_paths = []
    samples_dir_path = os.path.abspath(os.path.join(targeted_package, "samples"))
    package_name = os.path.basename(targeted_package)

    for path, subdirs, files in os.walk(samples_dir_path):
        for name in files:
            if fnmatch(name, "*.py") and name not in IGNORED_SAMPLES.get(package_name, []):
                sample_paths.append(os.path.abspath(os.path.join(path, name)))

    if not sample_paths:
        logging.info(
            "No samples found in {}".format(targeted_package)
        )
        exit(0)

    for sample in sample_paths:
        if sys.version_info < (3, 5) and sample.endswith("_async.py"):
            continue

        logging.info(
            "Testing {}".format(sample)
        )
        command_array = [sys.executable, sample]
        errors = run_check_call(command_array, root_dir, always_exit=False)

        sample_name = os.path.basename(sample)
        if errors:
            samples_errors.append(sample_name)
            logging.info(
                "ERROR: {}".format(sample_name)
            )
        else:
            logging.info(
                "SUCCESS: {}.".format(sample_name)
            )

    if samples_errors:
        logging.error("Sample(s) that ran with errors: {}".format(samples_errors))
        exit(1)

    logging.info(
        "All samples ran successfully in {}".format(targeted_package)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Dependencies, Install Packages, Test Azure Packages' Samples, Called from DevOps YAML Pipeline"
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run mypy will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()

    service_dir = os.path.join("sdk", args.target_package)
    target_dir = os.path.join(root_dir, service_dir)

    logging.info("User opted to run samples")

    run_samples(target_dir)
