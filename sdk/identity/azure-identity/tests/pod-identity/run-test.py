# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Deploys the test app and prints its output."""

import argparse
import os
import subprocess
import sys
import time

JOB_NAME = "test"
HELM_APP_NAME = "test"

parser = argparse.ArgumentParser()
parser.add_argument("--client-id", required=True, help="managed identity's client ID")
parser.add_argument("--resource-id", required=True, help="managed identity's ARM ID")
parser.add_argument("--vault-url", required=True, help="URL of a vault whose secrets the managed identity may manage")
parser.add_argument("--verbose", "-v", action="store_true", help="print all executed commands and their output")

image_options = parser.add_argument_group("image", "image options")
image_options.add_argument("--repository", required=True, help="repository holding the test image")
image_options.add_argument("--image-name", required=True, help="name of the test image")
image_options.add_argument("--image-tag", required=True, help="test image tag")

args = parser.parse_args()


def run_command(command, exit_on_failure=True):
    try:
        if args.verbose:
            print(" ".join(command))
        result = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip("'")
        if args.verbose:
            print(result)
        return result
    except subprocess.CalledProcessError as ex:
        result = ex.output.decode("utf-8").strip()
        if exit_on_failure:
            print(result)
            sys.exit(1)
        return result


# install the chart
helm_install = [
    "helm",
    "install",
    os.path.join(os.path.dirname(__file__), "test-pod-identity"),
    "-n",
    HELM_APP_NAME,
    "--set",
    "aad-pod-identity.azureIdentity.resourceID={},aad-pod-identity.azureIdentity.clientID={}".format(
        args.resource_id, args.client_id
    ),
    "--set",
    "vaultUrl=" + args.vault_url,
    "--set",
    "image.repository={},image.name={},image.tag={}".format(args.repository, args.image_name, args.image_tag),
]
run_command(helm_install)

# get the name of the test pod
pod_name = run_command(
    ["kubectl", "get", "pods", "--selector=job-name=" + JOB_NAME, "--output=jsonpath='{.items[*].metadata.name}'"]
)

logs = ""

# poll the number of active pods to determine when the test has finished
count_active_pods = ["kubectl", "get", "job", JOB_NAME, "--output=jsonpath='{.status.active}'"]
for _ in range(10):
    # kubectl will return '' when there are no active pods
    active_pods = run_command(count_active_pods)
    logs = run_command(["kubectl", "logs", "-f", pod_name], exit_on_failure=False)
    if not active_pods:
        break
    time.sleep(30)

# output logs from the most recent run
print(logs)

# uninstall the chart
run_command(["helm", "del", "--purge", HELM_APP_NAME])

# delete CRDs because Helm didn't
pod_identity_CRDs = [
    "azureassignedidentities.aadpodidentity.k8s.io",
    "azureidentities.aadpodidentity.k8s.io",
    "azureidentitybindings.aadpodidentity.k8s.io",
    "azurepodidentityexceptions.aadpodidentity.k8s.io",
]
run_command(["kubectl", "delete", "crd"] + pod_identity_CRDs)
