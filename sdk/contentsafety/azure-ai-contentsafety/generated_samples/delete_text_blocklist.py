# coding=utf-8

from azure.ai.contentsafety import BlocklistClient

"""
# PREREQUISITES
    pip install azure-ai-contentsafety
# USAGE
    python delete_text_blocklist.py
"""


def main():
    client = ContentSafetyClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.delete_text_blocklist(
        blocklist_name="TestBlocklist",
    )


# x-ms-original-file: 2024-09-01/DeleteTextBlocklist.json
if __name__ == "__main__":
    main()
