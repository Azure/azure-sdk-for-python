# coding=utf-8

from azure.appconfiguration import AzureAppConfigurationClient

"""
# PREREQUISITES
    pip install azure-appconfiguration
# USAGE
    python put_lock_if_match.py
"""


def main():
    client = AzureAppConfigurationClient(
        endpoint="https://{exampleAppConfigurationName}.azconfig.io",
        credential="CREDENTIAL",
    )

    response = client.put_lock(
        key="Message",
    )
    print(response)


# x-ms-original-file: 2023-11-01/PutLock_IfMatch.json
if __name__ == "__main__":
    main()
