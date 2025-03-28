# coding=utf-8

from azure.ai.translation.text import TextTranslationClient

"""
# PREREQUISITES
    pip install azure-ai-translation-text
# USAGE
    python get_supported_languages_minimum_set_gen.py
"""


def main():
    client = TextTranslationClient(
        endpoint="ENDPOINT",
    )

    response = client.get_supported_languages()
    print(response)


# x-ms-original-file: 3.0/GetSupportedLanguages_MinimumSet_Gen.json
if __name__ == "__main__":
    main()
