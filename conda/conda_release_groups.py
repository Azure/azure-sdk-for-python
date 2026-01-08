"""
Mapping of Azure SDK package names to their release group, used for Conda
release file updates in update_conda_files.py

New grouped packages should be registered before using the script
to update for Conda releases.

Packages that are not listed here are treated as standalone packages,
each forming their own release group (excluding mgmt packages, which will
by default be grouped).

Packages that are grouped together will:
  1. Share a single release log file (e.g., azure-communication.md for all communication packages)
  2. Be listed under one CondaArtifact entry in conda-sdk-client.yml
  3. Be released together under a single release parameter
"""

RELEASE_GROUPS = {
    # Core
    "azure-core": {
        "packages": ["azure-core", "azure-mgmt-core"],
        "common_root": "azure",
        "service": "core",
    },
    # Communication
    "azure-communication": {
        "packages": [
            "azure-communication-chat",
            "azure-communication-email",
            "azure-communication-identity",
            "azure-communication-phonenumbers",
            "azure-communication-sms",
            "azure-communication-callautomation",
            "azure-communication-rooms",
            "azure-communication-jobrouter",
            "azure-communication-messages",
        ],
        "common_root": "azure/communication",
        "service": "communication",
    },
    # Storage
    "azure-storage": {
        "packages": [
            "azure-storage-blob",
            "azure-storage-queue",
            "azure-storage-file-share",
            "azure-storage-file-datalake",
        ],
        "common_root": "azure/storage",
        "service": "storage",
    },
    # Schema Registry
    "azure-schemaregistry": {
        "packages": [
            "azure-schemaregistry",
            "azure-schemaregistry-avroencoder",
        ],
        "common_root": "azure/schemaregistry",
        "service": "schemaregistry",
    },
    # Event Hub
    "azure-eventhub": {
        "packages": [
            "azure-eventhub",
            "azure-eventhub-checkpointstoreblob",
            "azure-eventhub-checkpointstoreblob-aio",
        ],
        "common_root": "azure/eventhub",
        "service": "eventhub",
    },
    "azure-keyvault": {
        "packages": [
            "azure-keyvault-administration",
            "azure-keyvault-secrets",
            "azure-keyvault-keys",
            "azure-keyvault-certificates",
        ],
        "common_root": "azure/keyvault",
        "service": "keyvault",
    },
    # Packages with other pattern exceptions, e.g. different common root
    # or service vs package name mismatch
    "msrest": {"packages": ["msrest"], "common_root": None},
    "msal": {"packages": ["msal"], "common_root": None},
    "msal-extensions": {
        "packages": ["msal-extensions"],
        "common_root": "msal",
    },
    "azure-ai-vision": {
        "packages": ["azure-ai-vision-imageanalysis"],
        "common_root": "azure/vision",
    },
    "azure-healthinsights": {
        "packages": ["azure-healthinsights-radiology-insights"],
        "common_root": "azure",
        "service": "healthinsights",
    },
}


# Reverse mapping: package name -> release group name
def get_package_to_group_mapping():
    mapping = {}
    for group_name, group_info in RELEASE_GROUPS.items():
        for package in group_info["packages"]:
            mapping[package] = group_name
    return mapping


def get_release_group(package_name: str, package_to_group: dict) -> str:
    """
    Get the release group name for a given package.

    :param package_name: The package name (e.g., "azure-core", "azure-communication-chat")
    :return: The release group name (e.g., "azure-core", "azure-communication"), or package name itself if not grouped
    """
    return package_to_group.get(package_name, package_name)


def get_package_group_data(group_name: str) -> dict:
    """
    Get all packages that belong to a release group.

    :param group_name: The release group name
    :return: The group data dictionary, or empty dict if not found
    """
    return RELEASE_GROUPS.get(group_name, {})
