# coding=utf-8

from azure.ai.contentsafety import BlocklistClient

"""
# PREREQUISITES
    pip install azure-ai-contentsafety
# USAGE
    python get_text_blocklist_item.py
"""


def main():
    client = ContentSafetyClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.get_text_blocklist_item(
        blocklist_name="TestBlocklist",
        blocklist_item_id="9511969e-f1e3-4604-9127-05ee16c509ec",
    )
    print(response)


# x-ms-original-file: 2024-09-01/GetTextBlocklistItem.json
if __name__ == "__main__":
    main()
