import pytest
import os
import pathlib
import base64
import json

from azure.ai.evaluation._common.utils import nltk_tokenize


@pytest.mark.unittest
class TestUtils:
    def test_nltk_tokenize(self):

        # Test with English text
        text = "The capital of China is Beijing."
        tokens = nltk_tokenize(text)

        assert tokens == ["The", "capital", "of", "China", "is", "Beijing", "."]

        # Test with Multi-language text
        text = "The capital of China is 北京."
        tokens = nltk_tokenize(text)

        assert tokens == ["The", "capital", "of", "China", "is", "北京", "."]

    def convert_json_list_to_jsonl(self, project_scope, azure_cred):

        parent = pathlib.Path(__file__).parent.resolve()
        path = os.path.join(parent, "data")
        image_path = os.path.join(path, "image1.jpg")

        with pathlib.Path(image_path).open("rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        conversation = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            },
        ]

        messages = [{"messages": conversation}]
        datafile_jsonl_path = os.path.join(path, "datafile.jsonl")
        with open(datafile_jsonl_path, "w") as outfile:
            for json_obj in messages:
                json_line = json.dumps(json_obj)
                outfile.write(json_line + "\n")
