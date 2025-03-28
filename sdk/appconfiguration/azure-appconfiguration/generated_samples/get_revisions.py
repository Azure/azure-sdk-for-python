# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python get_revisions.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.get_revisions()
    for item in response:
        print(item)


# x-ms-original-file: 2023-11-01/GetRevisions.json
if __name__ == "__main__":
    main()
