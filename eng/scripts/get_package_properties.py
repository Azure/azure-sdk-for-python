import argparse
import os
import re

from typing import Dict, List

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import PATHS_EXCLUDED_FROM_DISCOVERY

additional_pr_triggers: Dict[str, List[str]] = {
    "azure-core":[
        "/sdk/servicebus/azure-servicebus",
        "/sdk/eventhub/azure-eventhub",
        "/sdk/tables/azure-data-tables",
        "/sdk/appconfiguration/azure-appconfiguration",
        "/sdk/keyvault/azure-keyvault-keys",
        "/sdk/identity/azure-identity",
        "/sdk/core/azure-mgmt-core",
        "/sdk/core/azure-core-experimental",
        "/sdk/core/azure-core-tracing-opentelemetry",
        "/sdk/core/azure-core-tracing-opencensus",
        # todo: this currently won't be included, as azure-cosmos needs some special construction
        # related to windows only + emulator
        # "/sdk/cosmos/azure-cosmos",
        "/sdk/ml/azure-ai-ml",
        "/sdk/documentintelligence/azure-ai-documentintelligence",
        "/sdk/ai/azure-ai-inference",
        "/sdk/textanalytics/azure-ai-textanalytics",
        "/sdk/translation/azure-ai-translation-document",
        "/sdk/compute/azure-mgmt-compute",
        "/sdk/communication/azure-communication-chat",
        "/sdk/communication/azure-communication-identity",
        "/sdk/storage/azure-storage-blob"
    ],
    "azure-mgmt-core": [
        "/sdk/compute/azure-mgmt-compute",
        "/sdk/network/azure-mgmt-network",
        "/sdk/resources/azure-mgmt-resource",
        "/sdk/keyvault/azure-mgmt-keyvault"
    ]
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get package version details from the repo")
    parser.add_argument("-s", "--search_path", required=True, help="The scope of the search")
    args = parser.parse_args()

    # Use abspath for the os.walk because if setup parsing fails it often changes cwd which throws off the relative walk
    for root, dirs, files in os.walk(os.path.abspath(args.search_path)):
        if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
            if "setup.py" in files or "pyproject.toml" in files:
                try:
                    parsed = ParsedSetup.from_path(root)

                    # Remove any packages excluded from discovery
                    # Skip packages whose folder path matches any entry in PATHS_EXCLUDED_FROM_DISCOVERY.
                    # PATHS_EXCLUDED_FROM_DISCOVERY contains subpaths (eg. "sdk/foo/bar") relative to repo root.
                    parsed_folder_norm = parsed.folder.replace("\\", "/")
                    if any(excluded_path in parsed_folder_norm for excluded_path in PATHS_EXCLUDED_FROM_DISCOVERY):
                        continue
                    
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
