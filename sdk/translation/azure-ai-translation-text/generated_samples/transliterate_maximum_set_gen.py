# coding=utf-8

from azure.ai.translation.text import TextTranslationClient

"""
# PREREQUISITES
    pip install azure-ai-translation-text
# USAGE
    python transliterate_maximum_set_gen.py
"""


def main():
    client = TextTranslationClient(
        endpoint="ENDPOINT",
    )

    response = client.transliterate(
        body=[{"text": "这是个测试。"}],
        language="zh-Hans",
        from_script="Hans",
        to_script="Latn",
    )
    print(response)


# x-ms-original-file: 3.0/Transliterate_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
