# coding=utf-8

from azure.ai.translation.text import TextTranslationClient

"""
# PREREQUISITES
    pip install azure-ai-translation-text
# USAGE
    python lookup_dictionary_entries_minimum_set_gen.py
"""


def main():
    client = TextTranslationClient(
        endpoint="ENDPOINT",
    )

    response = client.lookup_dictionary_entries(
        body=[{"text": "fly"}],
        from_language="en",
        to_language="es",
    )
    print(response)


# x-ms-original-file: 3.0/LookupDictionaryEntries_MinimumSet_Gen.json
if __name__ == "__main__":
    main()
