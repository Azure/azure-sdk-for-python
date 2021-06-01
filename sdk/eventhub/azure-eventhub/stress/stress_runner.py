# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from sys import platform
import configparser
from subprocess import Popen
from typing import cast
from datetime import datetime, timedelta
import time
import logging

from azure.storage.blob import BlobServiceClient
from azure.servicebus.control_client import ServiceBusService, EventHub


SEND_SCRIPT_PATH = "./azure_eventhub_producer_stress.py"
RECEIVE_SYNC_SCRIPT_PATH = "./azure_eventhub_consumer_stress_sync.py"
RECEIVE_ASYNC_SCRIPT_PATH = "./azure_eventhub_consumer_stress_async.py"


def parse_eventhub_conn_str(conn_str):
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None
    for element in conn_str.split(";"):
        key, _, value = element.partition("=")
        if key.lower() == "endpoint":
            endpoint = value.rstrip("/")
        elif key.lower() == "hostname":
            endpoint = value.rstrip("/")
        elif key.lower() == "sharedaccesskeyname":
            shared_access_key_name = value
        elif key.lower() == "sharedaccesskey":
            shared_access_key = value
        elif key.lower() == "entitypath":
            entity_path = value
    if not all([endpoint, shared_access_key_name, shared_access_key]):
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>"
        )
    entity = cast(str, entity_path)
    left_slash_pos = cast(str, endpoint).find("//")
    if left_slash_pos != -1:
        host = cast(str, endpoint)[left_slash_pos + 2 :]
    else:
        host = str(endpoint)
    namespace = host.split(".")[0]
    return host, namespace, str(shared_access_key_name), str(shared_access_key), entity


def create_stress_blob(stress_config, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(
        stress_config["CREDENTIALS"]["AZURE_STORAGE_CONN_STR"]
    )
    try:
        blob_service_client.delete_container(blob_name)
    except:
        pass
    create_succeed = False
    while not create_succeed:
        try:
            blob_service_client.create_container(blob_name)
            create_succeed = True
        except:
            pass
    return blob_name


def create_stress_eventhub(stress_config, eventhub_name):
    hub_value = EventHub(
        message_retention_in_days=stress_config["BASIC_CONFIG"]["message_retention_in_days"],
        partition_count=stress_config["BASIC_CONFIG"]["partition_cnt_to_create"]
    )
    if stress_config["CREDENTIALS"]["EVENT_HUB_CONN_STR"]:
        _, namespace, shared_access_key_name, shared_access_key, _ = parse_eventhub_conn_str(stress_config["CREDENTIALS"]["EVENT_HUB_CONN_STR"])
        client = ServiceBusService(
            service_namespace=namespace,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key
        )
    else:
        client = ServiceBusService(
            service_namespace=stress_config["CREDENTIALS"]["EVENT_HUB_NAMESPACE"],
            shared_access_key_name=stress_config['CREDENTIALS']["EVENT_HUB_SAS_POLICY"],
            shared_access_key_value=stress_config['CREDENTIALS']["EVENT_HUB_SAS_KEY"]
        )
    client.delete_event_hub(eventhub_name)
    if client.create_event_hub(eventhub_name, hub=hub_value, fail_on_exist=True):
        return eventhub_name
    raise ValueError("EventHub creation failed.")


def create_resource_for_task_if_needed(stress_config, task_name):
    if "large_partitions" in task_name or (not stress_config["BASIC_CONFIG"].getboolean("create_new_eventhub")):
        print("    ---- No resources would be created, using existing resources.")
        return (
            stress_config["CREDENTIALS"]["EVENT_HUB_NAME"],
            stress_config["CREDENTIALS"]["AZURE_STORAGE_BLOB_CONTAINER_NAME"]
        )

    resource_name = str.replace(task_name, "_", "-")
    eventhub_name, blob_name = None, None
    if "send" in task_name:
        print("    ---- New eventhub creating...")
        eventhub_name = create_stress_eventhub(stress_config, resource_name)
        print("    ---- New eventhub {} is created.".format(eventhub_name))
    if "checkpointstore" in task_name:
        print("    ---- New blob creating...")
        blob_name = create_stress_blob(stress_config, resource_name)
        print("    ---- New blob {} created.".format(blob_name))

    return eventhub_name, blob_name


def generate_base_send_command(task_name):
    partial_command = "python {}".format(SEND_SCRIPT_PATH)
    partial_command += " -m {}".format("stress_send_async" if "async" in task_name else "stress_send_sync")
    return partial_command


def generate_base_receive_command(task_name):
    partial_command = "python {}".format(
        RECEIVE_ASYNC_SCRIPT_PATH if "async" in task_name else RECEIVE_SYNC_SCRIPT_PATH
    )
    return partial_command


def generate_command_basic_config(basic_config):
    partial_command = ""
    partial_command += (" --duration {}".format(basic_config["duration"]))
    if basic_config.getboolean("print_console"):
        partial_command += " --print_console"
    partial_command += (" --auth_timeout {}".format(basic_config["auth_timeout"]))
    partial_command += (" --output_interval {}".format(basic_config["output_interval"]))
    return partial_command


def generate_command_send_config(send_config, proxy_config):
    partial_command = ""
    if send_config["parallel_send_cnt"]:
        partial_command += (" --parallel_send_cnt {}".format(send_config["parallel_send_cnt"]))
        if send_config["parallel_create_new_client"] and send_config.getboolean("parallel_create_new_client"):
            partial_command += " --parallel_create_new_client"
    partial_command += (" --payload {}".format(send_config["payload"]))
    partial_command += (" --partitions {}".format(send_config["partitions"]))
    if send_config.getboolean("uamqp_logging_enable"):
        partial_command += " --uamqp_logging_enable"
    if send_config.getboolean("use_http_proxy"):
        partial_command += (
            " --proxy_hostname {} --proxy_port {} --proxy_username {} --proxy_password {}".format(
                proxy_config["proxy_hostname"],
                proxy_config["proxy_port"],
                proxy_config["proxy_username"],
                proxy_config["proxy_password"]
            )
        )
    partial_command += (" --transport_type {}".format(send_config["transport_type"]))
    if send_config["retry_total"]:
        partial_command += (" --retry_total {}".format(send_config["retry_total"]))
    if send_config["retry_backoff_factor"]:
        partial_command += (" --retry_backoff_factor {}".format(send_config["retry_backoff_factor"]))
    if send_config["retry_backoff_max"]:
        partial_command += (" --retry_backoff_max {}".format(send_config["retry_backoff_max"]))
    if send_config.getboolean("ignore_send_failure"):
        partial_command += " --ignore_send_failure"
    return partial_command


def generate_command_receive_config(receive_config, proxy_config):
    partial_command = ""
    partial_command += " --link_credit {}".format(receive_config["link_credit"])
    if receive_config["consumer_group"]:
        partial_command += " --consumer_group {}".format(receive_config["consumer_group"])
    if receive_config["starting_offset"]:
        partial_command += " --starting_offset {}".format(receive_config["starting_offset"])
    if receive_config["starting_sequence_number"]:
        partial_command += " --starting_sequence_number {}".format(receive_config["starting_sequence_number"])
    if receive_config["starting_datetime"]:
        partial_command += " --starting_datetime \"{}\"".format(receive_config["starting_datetime"])
    partial_command += " --partitions {}".format(receive_config["partitions"])
    partial_command += " --load_balancing_interval {}".format(receive_config["load_balancing_interval"])
    partial_command += " --transport_type {}".format(receive_config["transport_type"])

    if receive_config.getboolean("track_last_enqueued_event_properties"):
        partial_command += " --track_last_enqueued_event_properties"
    if receive_config.getboolean("uamqp_logging_enable"):
        partial_command += " --uamqp_logging_enable"
    if receive_config.getboolean("use_http_proxy"):
        partial_command += (
            " --proxy_hostname {} --proxy_port {} --proxy_username {} --proxy_password {}".format(
                proxy_config["proxy_hostname"],
                proxy_config["proxy_port"],
                proxy_config["proxy_username"],
                proxy_config["proxy_password"]
            )
        )

    if receive_config["parallel_recv_cnt"]:
        partial_command += " --parallel_recv_cnt".format(receive_config["parallel_recv_cnt"])
    if receive_config["recv_partition_id"]:
        partial_command += " --recv_partition_id".format(receive_config["recv_partition_id"])

    return partial_command


def generate_command_resource_config(credential_config, eventhub_name, blob_name=None):
    partial_command = ""
    # EventHub Configuration
    if credential_config["EVENT_HUB_CONN_STR"]:
        partial_command += " --conn_str \"{}\"".format(credential_config["EVENT_HUB_CONN_STR"])
    if credential_config["EVENT_HUB_HOSTNAME"]:
        partial_command += "--hostname {}".format(credential_config["EVENT_HUB_HOSTNAME"])
    if eventhub_name or credential_config["EVENT_HUB_NAME"]:
        partial_command += " --eventhub {}".format(eventhub_name or credential_config["EVENT_HUB_NAME"])
    if credential_config["EVENT_HUB_SAS_POLICY"]:
        partial_command += " --sas-policy {}".format(credential_config["EVENT_HUB_SAS_POLICY"])
    if credential_config["EVENT_HUB_SAS_KEY"]:
        partial_command += " --sas-key {}".format(credential_config["EVENT_HUB_SAS_KEY"])
    if credential_config["AZURE_CLIENT_SECRET"]:
        partial_command += " --aad_secret {}".format(credential_config["AZURE_CLIENT_SECRET"])
    if credential_config["AZURE_CLIENT_ID"]:
        partial_command += " --aad_client_id {}".format(credential_config["AZURE_CLIENT_ID"])
    if credential_config["AZURE_TENANT_ID"]:
        partial_command += " --aad_tenant_id {}".format(credential_config["AZURE_TENANT_ID"])

    # Blob Configuration
    if blob_name:
        if credential_config["AZURE_STORAGE_CONN_STR"]:
            partial_command += " --storage_conn_str \"{}\"".format(credential_config["AZURE_STORAGE_CONN_STR"])
        partial_command += " --storage_container_name \"{}\"".format(blob_name)

    return partial_command


def generate_running_command(task_name, stress_config, eventhub_name, blob_name):
    commands = []

    if "send" in task_name:
        send_command = generate_base_send_command(task_name)
        send_command += generate_command_resource_config(stress_config["CREDENTIALS"], eventhub_name, None)
        send_command += generate_command_basic_config(stress_config["BASIC_CONFIG"])
        send_command += generate_command_send_config(
            stress_config["EVENTHUB_SEND_CONFIG"],
            stress_config["PROXY"]
        )
        send_command += " --log_filename \"{}_send.log\"".format(task_name)
        commands.append(send_command)

    if "receive" in task_name:
        receive_command = generate_base_receive_command(task_name)
        receive_command += generate_command_resource_config(stress_config["CREDENTIALS"], eventhub_name, blob_name)
        receive_command += generate_command_basic_config(stress_config["BASIC_CONFIG"])
        receive_command += generate_command_receive_config(
            stress_config["EVENTHUB_RECEIVE_CONFIG"],
            stress_config["PROXY"]
        )
        receive_command += " --log_filename \"{}_recv.log\"".format(task_name)
        commands.append(receive_command)

    return commands


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./stress_runner.cfg")

    target_stress_method = [m for m in config['RUN_METHODS'] if config['RUN_METHODS'].getboolean(m)]

    print("#### The following methods will be tested:")

    for method in target_stress_method:
        print("    ---- ", method)

    print("#### Creating resources started.")
    resources = [create_resource_for_task_if_needed(config, task) for task in target_stress_method]
    print("#### Creating resources done.")

    print("#### Generating commands started.")
    python_commands = []
    for i in range(len(target_stress_method)):
        python_commands.extend(
            generate_running_command(
                target_stress_method[i],
                config,
                resources[i][0],
                resources[i][1]
            )
        )

    for command in python_commands:
        print("    ---- ", command)

    print("#### Generating commands done.")

    if config['BASIC_CONFIG'].getboolean("run_generated_commands"):
        for command in python_commands:
            Popen(command, shell=(platform != "win32"))

        print("#### All the process has been started!")

    duration = int(config["BASIC_CONFIG"]["duration"]) + 600

    now = datetime.now()
    end = now + timedelta(seconds=duration)
    while now < end:
        # The while loop is to prevent container from being stopped
        now = datetime.now()
        logging.info("{}: Stress runner is running.".format(now))
        time.sleep(60)
