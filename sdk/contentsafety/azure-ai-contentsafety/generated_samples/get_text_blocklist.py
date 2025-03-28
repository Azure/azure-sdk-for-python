# coding=utf-8

from azure.ai.contentsafety import BlocklistClient

"""
# PREREQUISITES
    pip install azure-ai-contentsafety
# USAGE
    python get_text_blocklist.py
"""


def main():
    client = ContentSafetyClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.get_text_blocklist(
        blocklist_name="TestBlocklist",
    )
    print(response)


# x-ms-original-file: 2024-09-01/GetTextBlocklist.json
if __name__ == "__main__":
    main()
