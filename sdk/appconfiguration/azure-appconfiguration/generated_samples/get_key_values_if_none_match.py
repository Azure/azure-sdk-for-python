# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python get_key_values_if_none_match.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.get_key_values()
    for item in response:
        print(item)


# x-ms-original-file: 2023-11-01/GetKeyValues_IfNoneMatch.json
if __name__ == "__main__":
    main()
