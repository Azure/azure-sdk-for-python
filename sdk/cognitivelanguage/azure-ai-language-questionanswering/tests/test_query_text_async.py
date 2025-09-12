# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import AnswersFromTextOptions, TextDocument
from azure.core.credentials import AzureKeyCredential

from testcase import QuestionAnsweringTestCase


class TestQueryTextAsync(QuestionAnsweringTestCase):
    """Async tests covering:
    - Direct operations call via client.question_answering (LLC style)
    - Convenience wrapper client.get_answers_from_text
    - Dict input normalization (records list of dicts / strings)
    - Overload validation (mutually exclusive positional vs kwargs)
    """

    @pytest.mark.asyncio
    async def test_query_text_llc(self, recorded_test, qna_creds):
        # Use the public operations property (no internal build_* helpers)
        async with QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])) as client:
            options = AnswersFromTextOptions(
                question="What is the meaning of life?",
                text_documents=[
                    TextDocument(text="abc Graphics  Surprise, surprise -- our 4K  ", id="doc1"),
                    TextDocument(
                        text=(
                            "e graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up "
                            "from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped "
                            "Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading "
                            "to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface "
                            "Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't "
                            "meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU "
                            "in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on  "
                        ),
                        id="doc2",
                    ),
                    TextDocument(
                        text=(
                            "Graphics  Surprise, surprise -- our 4K Envy 13 came with a discrete graphics card. While the Nvidia GeForce "
                            "MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it "
                            "to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited "
                            "benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better "
                            "performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop "
                            "average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from "
                            "integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model."
                        ),
                        id="doc3",
                    ),
                ],
                language="en",
            )
            result = await client.question_answering.get_answers_from_text(options)
            assert result.answers
            for answer in result.answers:
                assert answer.answer
                assert answer.confidence is not None
                assert answer.id
                assert answer.offset is not None
                assert answer.length
                if answer.short_answer:  # short answer is optional on raw operations path
                    assert answer.short_answer.text
                    assert answer.short_answer.confidence is not None
                    assert answer.short_answer.offset is not None
                    assert answer.short_answer.length is not None

    @pytest.mark.asyncio
    async def test_query_text(self, recorded_test, qna_creds):
        async with QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])) as client:
            params = AnswersFromTextOptions(
                question="What is the meaning of life?",
                text_documents=[
                    TextDocument(text="abc Graphics  Surprise, surprise -- our 4K  ", id="doc1"),
                    TextDocument(
                        text=(
                            "e graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on the MX250 model, which is well above our 30-fps playability, the category average (69 fps) and what the Surface Laptop 2 (82 fps) achieved. The ZenBook S UX391UA (45 fps) fell flat on this real-world test but ran better than the base model Envy 13 (31 fps)."
                        ),
                        id="doc3",
                    ),
                ],
                language="en",
            )
            output = await client.get_answers_from_text(params)
            assert output.answers
            for answer in output.answers:
                assert answer.answer
                assert answer.confidence is not None
                assert answer.id
                assert answer.offset is not None      # was: assert answer.offset
                assert answer.length
                if answer.short_answer:
                    assert answer.short_answer.text
                    assert answer.short_answer.confidence is not None
                    assert answer.short_answer.offset is not None
                    assert answer.short_answer.length is not None

    @pytest.mark.asyncio
    async def test_query_text_with_dictparams(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = {
            "question": "How long it takes to charge surface?",
            "records": [
                {
                    "text": (
                        "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. "
                        "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it."
                    ),
                    "id": "1",
                },
                {
                    "text": (
                        "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "
                        "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface."
                    ),
                    "id": "2",
                },
            ],
            "language": "en",
        }

        async with client:
            output = await client.get_answers_from_text(params)
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @pytest.mark.asyncio
    async def test_query_text_with_str_records(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = {
            "question": "How long it takes to charge surface?",
            "records": [
                (
                    "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. "
                    "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it."
                ),
                (
                    "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "
                    "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface."
                ),
            ],
            "language": "en",
        }

        async with client:
            output = await client.get_answers_from_text(params)
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @pytest.mark.asyncio
    async def test_query_text_overload(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))

        async with client:
            with pytest.raises(TypeError):
                await client.get_answers_from_text(
                    question="How long it takes to charge surface?",
                    text_documents=[
                        (
                            "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. "
                            "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it."
                        ),
                        {
                            "text": (
                                "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "
                                "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface."
                            ),
                            "id": "2",
                        },
                    ],
                )
            output = await client.get_answers_from_text(
                question="How long it takes to charge surface?",
                text_documents=[
                    (
                        "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. "
                        "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it."
                    ),
                    (
                        "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "
                        "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface."
                    ),
                ],
            )
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @pytest.mark.asyncio
    async def test_query_text_overload_positional_and_kwarg(self):
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                await client.get_answers_from_text("positional_one", "positional_two")
            with pytest.raises(TypeError):
                await client.get_answers_from_text("positional_options_bag", options="options bag by name")
