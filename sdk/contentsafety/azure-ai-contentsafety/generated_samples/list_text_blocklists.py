# coding=utf-8

from azure.ai.contentsafety import BlocklistClient

"""
# PREREQUISITES
    pip install azure-ai-contentsafety
# USAGE
    python list_text_blocklists.py
"""


def main():
    client = ContentSafetyClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.list_text_blocklists()
    for item in response:
        print(item)


# x-ms-original-file: 2024-09-01/ListTextBlocklists.json
if __name__ == "__main__":
    main()
