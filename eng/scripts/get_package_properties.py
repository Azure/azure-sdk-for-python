import argparse
import os
import re

from typing import Dict, List

from ci_tools.parsing import ParsedSetup

additional_pr_triggers: Dict[str, List[str]] = {
    "azure-core":[
        os.path.join("/sdk", "servicebus", "azure-servicebus"),
        os.path.join("/sdk", "eventhub", "azure-eventhub"),
        os.path.join("/sdk", "tables", "azure-data-tables"),
        os.path.join("/sdk", "appconfiguration", "azure-appconfiguration"),
        os.path.join("/sdk", "keyvault", "azure-keyvault-keys"),
        os.path.join("/sdk", "identity", "azure-identity"),
        os.path.join("/sdk", "core", "azure-mgmt-core"),
        os.path.join("/sdk", "core", "azure-core-experimental"),
        os.path.join("/sdk", "core", "azure-core-tracing-opentelemetry"),
        os.path.join("/sdk", "core", "azure-core-tracing-opencensus"),
        # todo: this currently won't be included, as azure-cosmos needs some special construction
        # related to windows only + emulator
        # os.path.join("/sdk", "cosmos", "azure-cosmos"),
        os.path.join("/sdk", "ml", "azure-ai-ml"),
        os.path.join("/sdk", "documentintelligence", "azure-ai-documentintelligence"),
        os.path.join("/sdk", "ai", "azure-ai-inference"),
        os.path.join("/sdk", "textanalytics", "azure-ai-textanalytics"),
        os.path.join("/sdk", "translation", "azure-ai-translation-document"),
        os.path.join("/sdk", "compute", "azure-mgmt-compute"),
        os.path.join("/sdk", "communication", "azure-communication-chat"),
        os.path.join("/sdk", "communication", "azure-communication-identity"),
        os.path.join("/sdk", "storage", "azure-storage-blob")
    ],
    "azure-mgmt-core": [
        os.path.join("/sdk", "compute", "azure-mgmt-compute"),
        os.path.join("/sdk", "network", "azure-mgmt-network"),
        os.path.join("/sdk", "resources", "azure-mgmt-resource"),
        os.path.join("/sdk", "keyvault", "azure-mgmt-keyvault")
    ]
}

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
