# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python create_snapshot.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.begin_create_snapshot(
        name="Prod-2022-08-01",
        entity={"filters": [{"key": "app1/*", "label": "Production"}], "retention_period": 3600},
    ).result()
    print(response)


# x-ms-original-file: 2023-11-01/CreateSnapshot.json
if __name__ == "__main__":
    main()
