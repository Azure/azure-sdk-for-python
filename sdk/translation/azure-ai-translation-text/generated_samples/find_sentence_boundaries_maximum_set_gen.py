# coding=utf-8

from azure.ai.translation.text import TextTranslationClient

"""
# PREREQUISITES
    pip install azure-ai-translation-text
# USAGE
    python find_sentence_boundaries_maximum_set_gen.py
"""


def main():
    client = TextTranslationClient(
        endpoint="ENDPOINT",
    )

    response = client.find_sentence_boundaries(
        body=[{"text": "How are you? I am fine. What did you do today?"}],
    )
    print(response)


# x-ms-original-file: 3.0/FindSentenceBoundaries_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
