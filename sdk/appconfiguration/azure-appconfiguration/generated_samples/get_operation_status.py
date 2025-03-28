# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python get_operation_status.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.get_operation_details(
        snapshot="Prod-2022-08-01",
    )
    print(response)


# x-ms-original-file: 2023-11-01/GetOperationStatus.json
if __name__ == "__main__":
    main()
