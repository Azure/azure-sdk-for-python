# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python check_snapshot_if_none_match.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.check_snapshot(
        name="Prod-2022-08-01",
    )
    print(response)


# x-ms-original-file: 2023-11-01/CheckSnapshot_IfNoneMatch.json
if __name__ == "__main__":
    main()
