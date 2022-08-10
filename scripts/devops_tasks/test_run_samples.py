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

try:
    from subprocess import TimeoutExpired, check_call, CalledProcessError
except ImportError:
    from subprocess32 import TimeoutExpired, check_call, CalledProcessError
from common_tasks import run_check_call, compare_python_version

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

MINIMUM_TESTED_PYTHON_VERSION = ">=3.7.0"

"""
Some samples may "run forever" or need to be timed out after a period of time. Add them here in the following format:
TIMEOUT_SAMPLES = {
    "<package-name>": {
        "<sample_file_name.py>": (<timeout (seconds)>, <pass if timeout? (bool, default: True)>)
    }
}
"""
TIMEOUT_SAMPLES = {
    "azure-eventgrid": {
        "consume_cloud_events_from_storage_queue.py": (10),
    },
    "azure-eventhub": {
        "receive_batch_with_checkpoint.py": (10),
        "recv.py": (10),
        "recv_track_last_enqueued_event_prop.py": (10),
        "recv_with_checkpoint_by_event_count.py": (10),
        "recv_with_checkpoint_by_time_interval.py": (10),
        "recv_with_checkpoint_store.py": (10),
        "recv_with_custom_starting_position.py": (10),
        "sample_code_eventhub.py": (10),
        "receive_batch_with_checkpoint_async.py": (10),
        "recv_async.py": (10),
        "recv_track_last_enqueued_event_prop_async.py": (10),
        "recv_with_checkpoint_by_event_count_async.py": (10),
        "recv_with_checkpoint_by_time_interval_async.py": (10),
        "recv_with_checkpoint_store_async.py": (10),
        "recv_with_custom_starting_position_async.py": (10),
        "sample_code_eventhub_async.py": (10),
        "send_and_receive_amqp_annotated_message.py": (10),
        "send_and_receive_amqp_annotated_message_async.py": (10),
    },
    "azure-eventhub-checkpointstoreblob": {
        "receive_events_using_checkpoint_store.py": (10),
        "receive_events_using_checkpoint_store_storage_api_version.py": (10),
    },
    "azure-eventhub-checkpointstoreblob-aio": {
        "receive_events_using_checkpoint_store_async.py": (10),
        "receive_events_using_checkpoint_store_storage_api_version_async.py": (10),
    },
    "azure-servicebus": {
        "failure_and_recovery.py": (10),
        "receive_iterator_queue.py": (10),
        "sample_code_servicebus.py": (30),
        "session_pool_receive.py": (20),
        "receive_iterator_queue_async.py": (10),
        "sample_code_servicebus_async.py": (30),
        "session_pool_receive_async.py": (20),
    },
}


# Add your library + sample file if you do not want a particular sample to be run
IGNORED_SAMPLES = {
    "azure-eventgrid": [
        "__init__.py",
        "consume_cloud_events_from_eventhub.py",
        "consume_eventgrid_events_from_service_bus_queue.py",
        "sample_publish_events_to_a_topic_using_sas_credential.py",
        "sample_publish_events_to_a_topic_using_sas_credential_async.py"
    ],
    "azure-eventhub": [
        "connection_to_custom_endpoint_address.py",
        "proxy.py",
        "connection_to_custom_endpoint_address_async.py",
        "iot_hub_connection_string_receive_async.py",
        "proxy_async.py",
    ],
    "azure-eventhub-checkpointstoretable": ["receive_events_using_checkpoint_store.py"],
    "azure-servicebus": [
        "connection_to_custom_endpoint_address.py",
        "mgmt_queue.py",
        "mgmt_rule.py",
        "mgmt_subscription.py",
        "mgmt_topic.py",
        "proxy.py",
        "receive_deferred_message_queue.py",
        "connection_to_custom_endpoint_address_async.py",
        "mgmt_queue_async.py",
        "mgmt_rule_async.py",
        "mgmt_subscription_async.py",
        "mgmt_topic_async.py",
        "proxy_async.py",
        "receive_deferred_message_queue_async.py",
    ],
    "azure-communication-chat": [
        "chat_client_sample_async.py",
        "chat_client_sample.py",
        "chat_thread_client_sample_async.py",
        "chat_thread_client_sample.py",
    ],
    "azure-communication-phonenumbers": [
        "purchase_phone_number_sample_async.py",
        "purchase_phone_number_sample.py",
        "release_phone_number_sample_async.py",
        "release_phone_number_sample.py",
    ],
    "azure-ai-translation-document": [
        "sample_list_document_statuses_with_filters_async.py",
        "sample_list_translations_with_filters_async.py",
        "sample_list_document_statuses_with_filters.py",
        "sample_list_translations_with_filters.py",
        "sample_translation_with_custom_model.py",
        "sample_translation_with_custom_model_async.py",
        "sample_begin_translation_with_filters.py",
        "sample_begin_translation_with_filters_async.py"
    ],
    "azure-ai-language-questionanswering": ["sample_chat.py"],
    "azure-ai-language-conversations": [
        "sample_import_train_deploy_project_async.py",
        "sample_import_train_deploy_project.py",
    ],
    "azure-ai-textanalytics": [
        "sample_analyze_healthcare_entities_with_cancellation.py",
        "sample_analyze_healthcare_entities_with_cancellation_async.py",
    ]
}

def run_check_call_with_timeout(
    command_array,
    working_directory,
    timeout,
    pass_if_timeout,
    acceptable_return_codes=[],
    always_exit=False,
):
    """This is copied from common_tasks.py with some additions.
    Don't want to break anyone that's using the original code.
    """
    try:
        logging.info(
            "Command Array: {0}, Target Working Directory: {1}".format(
                command_array, working_directory
            )
        )
        check_call(command_array, cwd=working_directory, timeout=timeout)
    except CalledProcessError as err:
        if err.returncode not in acceptable_return_codes:
            logging.error(err)  # , file = sys.stderr
            if always_exit:
                exit(1)
            else:
                return err
    except TimeoutExpired as err:
        if pass_if_timeout:
            logging.info("Sample timed out successfully")
        else:
            logging.info("Fail: Sample timed out")
            return err


def execute_sample(sample, samples_errors, timed):
    if isinstance(sample, tuple):
        sample, timeout, pass_if_timeout = sample

    if sys.version_info < (3, 5) and sample.endswith("_async.py"):
        return

    logging.info("Testing {}".format(sample))
    command_array = [sys.executable, sample]

    if not timed:
        errors = run_check_call(command_array, root_dir, always_exit=False)
    else:
        errors = run_check_call_with_timeout(
            command_array, root_dir, timeout, pass_if_timeout
        )

    sample_name = os.path.basename(sample)
    if errors:
        samples_errors.append(sample_name)
        logging.info("ERROR: {}".format(sample_name))
    else:
        logging.info("SUCCESS: {}.".format(sample_name))


def resolve_sample_ignore(sample_file, package_name):
    ignored_files = [
        (f, ">=2.7") if not isinstance(f, tuple) else f
        for f in IGNORED_SAMPLES.get(package_name, [])
    ]
    ignored_files_dict = {key: value for (key, value) in ignored_files}

    if sample_file in ignored_files_dict and compare_python_version(
        ignored_files_dict[sample_file]
    ):
        return False
    else:
        return True


def run_samples(targeted_package):
    logging.info("running samples for {}".format(targeted_package))

    samples_errors = []
    sample_paths = []
    timed_sample_paths = []

    samples_dir_path = os.path.abspath(os.path.join(targeted_package, "samples"))
    package_name = os.path.basename(targeted_package)
    samples_need_timeout = TIMEOUT_SAMPLES.get(package_name, {})

    # install extra dependencies for samples if needed
    try:
        with open(samples_dir_path + "/sample_dev_requirements.txt") as sample_dev_reqs:
            for dep in sample_dev_reqs.readlines():
                check_call([sys.executable, "-m", "pip", "install", dep])
    except IOError:
        pass

    for path, subdirs, files in os.walk(samples_dir_path):
        for name in files:
            if fnmatch(name, "*.py") and name in samples_need_timeout:
                timeout = samples_need_timeout[name]
                # timeout, pass_if_timeout is True by default if nothing passed in
                if isinstance(timeout, tuple):
                    timeout, pass_if_timeout = timeout
                else:
                    pass_if_timeout = True
                timed_sample_paths.append(
                    (
                        os.path.abspath(os.path.join(path, name)),
                        timeout,
                        pass_if_timeout,
                    )
                )
            elif fnmatch(name, "*.py") and resolve_sample_ignore(name, package_name):
                sample_paths.append(os.path.abspath(os.path.join(path, name)))

    if not sample_paths and not timed_sample_paths:
        logging.info("No samples found in {}".format(targeted_package))
        exit(0)

    for sample in sample_paths:
        execute_sample(sample, samples_errors, timed=False)

    for sample in timed_sample_paths:
        execute_sample(sample, samples_errors, timed=True)

    if samples_errors:
        logging.error("Sample(s) that ran with errors: {}".format(samples_errors))
        exit(1)

    logging.info("All samples ran successfully in {}".format(targeted_package))


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

    if compare_python_version(MINIMUM_TESTED_PYTHON_VERSION):
        logging.info(
            "User opted to run samples, and python version is greater than minimum supported."
        )
        run_samples(target_dir)
