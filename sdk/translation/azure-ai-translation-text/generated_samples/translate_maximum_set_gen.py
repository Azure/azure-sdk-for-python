# coding=utf-8

from azure.ai.translation.text import TextTranslationClient

"""
# PREREQUISITES
    pip install azure-ai-translation-text
# USAGE
    python translate_maximum_set_gen.py
"""


def main():
    client = TextTranslationClient(
        endpoint="ENDPOINT",
    )

    response = client.translate(
        body=[{"text": "This is a test."}],
        to_language=["cs"],
    )
    print(response)


# x-ms-original-file: 3.0/Translate_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
