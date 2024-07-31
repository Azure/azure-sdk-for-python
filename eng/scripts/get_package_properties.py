import argparse
import sys
import glob
import os
import re

from typing import Dict, List

from ci_tools.parsing import ParsedSetup

additional_pr_triggers: Dict[str, List[str]] = {
    "azure-core":[
        "sdk/storage/azure-storage-blob",
        "sdk/servicebus/azure-servicebus",
        "sdk/eventhub/azure-eventhub",
        "sdk/tables/azure-data-table",
        "sdk/appconfig/azure-appconfig",
        "sdk/keyvault/azure-keyvault-keys",
        "sdk/identity/azure-identity",
        "sdk/core/azure-mgmt-core",
        "sdk/core/azure-core-experimental",
        "sdk/core/azure-core-tracing-opentelemetry",
        "sdk/core/azure-core-tracing-opencensus",
        "sdk/cosmos/azure-cosmos",
        "sdk/ml/azure-ai-ml",
        "sdk/ai/azure-ai-documentintelligence",
        "sdk/ai/azure-ai-inference",
        "sdk/ai/azure-ai-textanalytics",
        "sdk/ai/azure-ai-doctranslation",
        "sdk/compute/azure-mgmt-compute",
        "sdk/communication/azure-communication-chat",
        "sdk/communication/azure-communication-identity",
    ],
    "azure-mgmt-core": [
        "sdk/compute/azure-mgmt-compute",
        "sdk/network/azure-mgmt-network",
        "sdk/resource/azure-mgmt-resource",
        "sdk/keyvault/azure-mgmt-keyvault",
    ]
}

# todo triggers based on paths and not files
# tools/
#   azure-storage-blob
#   azure-servicebus
#   azure-eventhub
#   azure-data-table
#   azure-appconfig
#   azure-keyvault-keys
#   azure-identity
#   azure-mgmt-core
#   azure-core-experimental
#   azure-core-tracing-opentelemetry
#   azure-core-tracing-opencensus
#   azure-cosmos
#   azure-ai-documentintelligence
#   azure-ai-ml
#   azure-ai-inference
#   azure-ai-textanalytics
#   azure-ai-doctranslation
#   azure-mgmt-compute
#   azure-communication-chat
#   azure-communication-identity

# eng/
#   azure-template
#   azure-core

# scripts/, doc/, common/, conda/
#   azure-template
#   azure-core


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get package version details from the repo")
    parser.add_argument("-s", "--search_path", required=True, help="The scope of the search")
    args = parser.parse_args()

    # Use abspath for the os.walk because if setup parsing fails it often changes cwd which throws off the relative walk
    for root, dirs, files in os.walk(os.path.abspath(args.search_path)):
        if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
            if "setup.py" in files:
                try:
                    parsed = ParsedSetup.from_path(root)

                    dependent_packages = ""
                    if parsed.name in additional_pr_triggers:
                        dependent_packages = ",".join(additional_pr_triggers[parsed.name])

                    print(
                        "{0} {1} {2} {3} {4}".format(
                            parsed.name,
                            parsed.version,
                            parsed.is_new_sdk,
                            os.path.dirname(parsed.setup_filename),
                            dependent_packages
                        )
                    )
                except:
                    # Skip setup.py if the package cannot be parsed
                    pass