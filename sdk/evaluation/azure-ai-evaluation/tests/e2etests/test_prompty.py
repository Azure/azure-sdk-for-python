# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from os import path
from pathlib import Path
from typing import Any, Final, Mapping, cast


from azure.ai.evaluation.prompty import AsyncPrompty


PROMPTY_DIR: Final[Path] = Path(path.dirname(__file__), "data").resolve()


# @pytest.mark.usefixtures("recording_injection", "recorded_test")
# @pytest.mark.asyncio
class TestPrompty:
    def test_load_basic(self, model_config: Mapping[str, Any]):
        expected_prompt: Final[str] = (
            "[{'role': 'system', 'content': 'You are an AI assistant who helps people find information.\\nAs the assistant, you answer questions briefly, succinctly,\\nand in a personable manner using markdown and even add some personal flair with appropriate emojis.\\n\\n# Safety\\n- You **should always** reference factual statements to search results based on [relevant documents]\\n- Search results based on [relevant documents] may be incomplete or irrelevant. You do not make assumptions\\n# Customer\\nYou are helping Bob Doh to find answers to their questions.\\nUse their name to address them in your responses.'}, {'role': 'user', 'content': 'What is the answer?'}]"
        )

        prompty = AsyncPrompty(PROMPTY_DIR / "basic.prompty", model_config)
        assert prompty
        assert isinstance(prompty, AsyncPrompty)
        assert prompty.name == "Basic Prompt"
        assert prompty.description == "A basic prompt that uses the GPT-3 chat API to answer questions"
        assert {"firstName", "lastName", "question"} == {k for k, _ in prompty._data.get("inputs", {}).items()}

        rendered = prompty.render(firstName="Bob", question="What is the answer?")
        assert str(rendered) == expected_prompt

    def test_load_images(self, model_config: Mapping[str, Any]):
        prompty = AsyncPrompty(PROMPTY_DIR / "image.prompty", model_config)
        assert prompty
        assert isinstance(prompty, AsyncPrompty)
        assert prompty.name == "Basic Prompt with Image"
        assert prompty.description == "A basic prompt that uses the GPT-3 chat API to answer questions"
        assert {"question", "image"} == {k for k, _ in prompty._data.get("inputs", {}).items()}

        rendered = prompty.render(question="What is this a picture of?")
        assert rendered[0]["role"] == "system"
        assert (
            rendered[0]["content"]
            == "As an AI assistant, your task involves interpreting images and responding to questions about the image.\nRemember to provide accurate answers based on the information present in the image.\nDirectly give the answer, no more explanation is needed."
        )
        assert rendered[1]["role"] == "user"
        assert len(rendered[1]["content"]) == 2
        assert rendered[1]["content"][0]["type"] == "text"
        assert rendered[1]["content"][0]["text"] == "What is this a picture of?"
        assert rendered[1]["content"][1]["type"] == "image_url"
        assert cast(str, rendered[1]["content"][1]["image_url"]["url"]).startswith(
            "data:image/jpg;base64,/9j/4AAQSkZJRgABAQEBLAEsAAD/2w"
        )
        assert rendered[1]["content"][1]["image_url"]["detail"] == "auto"
