# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python check_key_value.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.check_key_value(
        key="Message",
    )
    print(response)


# x-ms-original-file: 2023-11-01/CheckKeyValue.json
if __name__ == "__main__":
    main()
