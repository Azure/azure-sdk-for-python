# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python delete_key_value.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.delete_key_value(
        key="Message",
    )
    print(response)


# x-ms-original-file: 2023-11-01/DeleteKeyValue.json
if __name__ == "__main__":
    main()
