import configparser
from subprocess import Popen
from typing import cast

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient
from azure.servicebus.control_client import ServiceBusService, EventHub


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
        stress_config["AZURE_STORAGE_CONN_STR"])
    blob_service_client.create_container(blob_name)
    return blob_name


def create_stress_eventhub(stress_config, eventhub_name):
    hub_value = EventHub(
        message_retention_in_days=stress_config["BASIC_CONFIG"]["message_retention_in_days"],
        partition_count=["BASIC_CONFIG"]["partition_cnt_to_create"]
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
    if client.create_event_hub(eventhub_name, hub=hub_value, fail_on_exist=True):
        return eventhub_name
    raise ValueError("EventHub creation failed.")


def create_resource_for_task_if_needed(stress_config, task_name):
    if "large_partitions" in task_name or (not stress_config["BASIC_CONFIG"].getboolean("create_new_eventhub")):
        return

    resource_name = str.replace(task_name, "_", "-")
    eventhub_name, blob_name = None, None
    if "send" in task_name:
        eventhub_name = create_stress_eventhub(stress_config, resource_name)
    if "checkpointstore" in task_name:
        blob_name = create_stress_blob(stress_config, resource_name)

    return eventhub_name, blob_name


def generate_init_command(task_name):
    return ""


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
    if send_config.getboolean("uamqp_debug"):
        partial_command += " --uamqp_debug"
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
    return partial_command


def generate_command_receive_config(send_config):
    return ""


def generate_command_resource_config(credential_config, eventhub_name=None, blob_name=None):
    return ""


def generate_running_command(task_name, stress_config, eventhub_name, blob_name):
    commands = []

    basic_config = stress_config["BASIC_CONFIG"]
    send_config = stress_config["EVENTHUB_SEND_CONFIG"]
    receive_config = stress_config["EVENTHUB_RECEIVE_CONFIG"]
    proxy_config = stress_config["PROXY"]

    if "send" in task_name:
        command = "python ./azure_eventhub_producer_stress.py -m {}".format(
            "stress_send_sync" if "sync" in task_name else "stress_send_async"
        )

        commands.append(command)

    if "receive" in task_name:
        commands.append(command)
        pass

    commands = []
    command = generate_init_command(task_name)
    command += generate_command_resource_config(stress_config["CREDENTIALS"], eventhub_name, blob_name)
    command += generate_command_basic_config(stress_config["BASIC_CONFIG"])

    if "send" in task_name:
        send_command = command + generate_command_send_config(
            stress_config["EVENTHUB_SEND_CONFIG"],
            stress_config["PROXY"]
        )
        commands.append(send_command)

    if "receive" in task_name:
        receive_command = command + generate_command_receive_config(
            stress_config["EVENTHUB_RECEIVE_CONFIG"],
            stress_config["PROXY"]
        )
        commands.append(receive_command)

    return commands


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./stress_runner.cfg")

    target_stress_method = [m for m in config['RUN_METHODS'] if config['RUN_METHODS'].getboolean(m)]
    resources = [create_resource_for_task_if_needed(config, task) for task in target_stress_method ]

    commands = []
    for i in range(target_stress_method):
        commands.extend(
            generate_running_command(
                target_stress_method[i],
                config,
                resources[i][0],
                resources[i][1]
            )
        )

    for command in commands:
        Popen(command)
