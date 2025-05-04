# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import re
from collections import defaultdict
from os import path
from pathlib import Path
from typing import Any, AsyncGenerator, DefaultDict, Dict, Final, Mapping, Optional, cast

from openai.types.chat import ChatCompletion

from azure.ai.evaluation._legacy.prompty import AsyncPrompty, InvalidInputError
from azure.ai.evaluation import AzureOpenAIModelConfiguration


PROMPTY_TEST_DIR: Final[Path] = Path(path.dirname(__file__), "data").resolve()
EVALUATOR_ROOT_DIR: Final[Path] = Path(path.dirname(__file__), "../../azure/ai/evaluation/_evaluators").resolve()
BASIC_PROMPTY: Final[Path] = PROMPTY_TEST_DIR / "basic.prompty"
IMAGE_PROMPTY: Final[Path] = PROMPTY_TEST_DIR / "image.prompty"
JSON_PROMPTY: Final[Path] = PROMPTY_TEST_DIR / "json.prompty"
COHERENCE_PROMPTY: Final[Path] = EVALUATOR_ROOT_DIR / "_coherence" / "coherence.prompty"


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)


@pytest.fixture()
def prompty_config(model_config: AzureOpenAIModelConfiguration) -> DefaultDict[str, Any]:
    cloned_model: Dict[str, Any] = defaultdict(recursive_defaultdict)
    cloned_model.update({"type": "azure_openai", **model_config})

    config: DefaultDict[str, Any] = defaultdict(recursive_defaultdict)
    config["model"]["configuration"] = cloned_model
    return config


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestPrompty:
    def test_load_basic(self, prompty_config: Dict[str, Any]):
        expected_prompt: Final[str] = (
            "[{'role': 'system', 'content': 'You are an AI assistant who helps people find information.\\nAs the assistant, you answer questions briefly, succinctly,\\nand in a personable manner using markdown and even add some personal flair with appropriate emojis.\\n\\n# Safety\\n- You **should always** reference factual statements to search results based on [relevant documents]\\n- Search results based on [relevant documents] may be incomplete or irrelevant. You do not make assumptions\\n# Customer\\nYou are helping Bob Doh to find answers to their questions.\\nUse their name to address them in your responses.'}, {'role': 'user', 'content': 'What is the answer?'}]"
        )

        prompty = AsyncPrompty(BASIC_PROMPTY, **prompty_config)
        assert prompty
        assert isinstance(prompty, AsyncPrompty)
        assert prompty.name == "Basic Prompt"
        assert prompty.description == "A basic prompt that uses the GPT-3 chat API to answer questions"
        assert {"firstName", "lastName", "question"} == {k for k, _ in prompty._data.get("inputs", {}).items()}

        rendered = prompty.render(firstName="Bob", question="What is the answer?")
        assert str(rendered) == expected_prompt

    def test_load_images(self, prompty_config: Dict[str, Any]):
        prompty = AsyncPrompty(IMAGE_PROMPTY, **prompty_config)
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

    @pytest.mark.asyncio
    async def test_first_match_text(self, prompty_config: Dict[str, Any]):
        prompty = AsyncPrompty(COHERENCE_PROMPTY, **prompty_config)
        result = await prompty(query="What is the capital of France?", response="France capital Paris")

        # We expect an output string that contains <S0>chain of thoughts</S0> <S1>explanation<S1> <S2>int_score</S2>
        assert isinstance(result, str)
        matched = re.match(
            r"^\s*<S0>(.*)</S0>\s*<S1>(.*)</S1>\s*<S2>(.*)</S2>\s*$",
            result,
            re.MULTILINE | re.DOTALL,
        )
        assert matched
        assert isinstance(matched.group(1), str)
        assert isinstance(matched.group(2), str)
        score: int = int(matched.group(3))
        assert score >= 0 and score <= 5

    @pytest.mark.asyncio
    async def test_first_match_image(self, prompty_config: Dict[str, Any]):
        prompty = AsyncPrompty(IMAGE_PROMPTY, **prompty_config)
        result = await prompty(image="image1.jpg", question="What is this a picture of?")
        assert isinstance(result, str)
        assert "apple" in result.lower()

    @pytest.mark.asyncio
    async def test_first_match_text_streaming(self, prompty_config: Dict[str, Any]):
        prompty_config["model"]["parameters"]["stream"] = True
        prompty = AsyncPrompty(BASIC_PROMPTY, **prompty_config)
        result = await prompty(firstName="Bob", question="What is the capital of France?")

        assert isinstance(result, AsyncGenerator)
        combined = ""
        async for chunk in result:
            assert isinstance(chunk, str)
            combined += chunk

        assert "Paris" in combined
        assert "Bob" in combined

    @pytest.mark.asyncio
    async def test_first_match_image_streaming(self, prompty_config: Dict[str, Any]):
        prompty_config["model"]["parameters"]["stream"] = True
        prompty = AsyncPrompty(IMAGE_PROMPTY, **prompty_config)
        result = await prompty(image="image1.jpg", question="What is this a picture of?")

        assert isinstance(result, AsyncGenerator)
        combined = ""
        async for chunk in result:
            assert isinstance(chunk, str)
            combined += chunk

        assert "apple" in combined

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "outputs",
        [
            {},
            {"firstName": {"type": "str"}, "answer": {"type": "str"}},
        ],
    )
    async def test_first_match_text_json(self, prompty_config: Dict[str, Any], outputs: Mapping[str, Any]):
        prompty_config["outputs"] = outputs
        prompty = AsyncPrompty(JSON_PROMPTY, **prompty_config)
        result = await prompty(question="What is the capital of France?")

        assert isinstance(result, Mapping)
        assert "firstName" in result
        assert result["firstName"] == "John"
        assert "answer" in result
        assert "Paris" in result["answer"]

        if outputs:
            # Should ahve only first name, and answer
            assert "lastName" not in result
        else:
            assert "lastName" in result
            assert result["lastName"] == "Doh"

    @pytest.mark.asyncio
    async def test_first_match_text_json_missing(self, prompty_config: Dict[str, Any]):
        prompty_config["outputs"] = {"does_not_exist": {"type": "str"}}
        prompty = AsyncPrompty(JSON_PROMPTY, **prompty_config)
        with pytest.raises(InvalidInputError) as ex:
            await prompty(question="What is the capital of France?")
        assert "does_not_exist" in ex.value.message

    @pytest.mark.asyncio
    async def test_first_match_text_json_streaming(self, prompty_config: Dict[str, Any]):
        prompty_config["model"]["parameters"]["stream"] = True
        prompty = AsyncPrompty(JSON_PROMPTY, **prompty_config)
        result = await prompty(question="What is the capital of France?", firstName="Barbra", lastName="Streisand")
        assert isinstance(result, Mapping)
        assert result["firstName"] == "Barbra"
        assert result["lastName"] == "Streisand"
        assert "Paris" in result["answer"]

    @pytest.mark.asyncio
    async def test_full_text(self, prompty_config: Dict[str, Any]):
        prompty_config["model"]["response"] = "full"
        prompty = AsyncPrompty(BASIC_PROMPTY, **prompty_config)
        result = await prompty(firstName="Bob", question="What is the capital of France?")
        assert isinstance(result, ChatCompletion)
        response: str = result.choices[0].message.content or ""
        assert "Bob" in response
        assert "Paris" in response
