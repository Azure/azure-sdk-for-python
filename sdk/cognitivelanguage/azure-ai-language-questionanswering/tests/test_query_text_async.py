# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    QuestionAnsweringTest,
    GlobalQuestionAnsweringAccountPreparer
)

from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering._operations._operations import build_get_answers_from_text_request
from azure.ai.language.questionanswering.models import (
    AnswersFromTextOptions,
    TextDocument
)

class QnATests(QuestionAnsweringTest):
    def setUp(self):
        super(QnATests, self).setUp()

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text_llc(self, qna_account, qna_key):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        json_content = {
            "question": "What is the meaning of life?",
            "records": [
                {
                    "text": "abc Graphics  Surprise, surprise -- our 4K  ",
                    "id": "doc1"
                },
                {
                    "text": "e graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on  ",
                    "id": "doc2"
                },
                {
                    "text": "Graphics  Surprise, surprise -- our 4K Envy 13 came with a discrete graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on the MX250 model, which is well above our 30-fps playability, the category average (69 fps) and what the Surface Laptop 2 (82 fps) achieved. The ZenBook S UX391UA (45 fps) fell flat on this real-world test but ran better than the base model Envy 13 (31 fps).  Audio  I had a good ol' time groovin' to the sound of the Envy 13's crisp speakers. HP went all out with the Envy, placing dual speakers on the underside of the chassis along with a third, top-firing driver above the keyboard. Devon Gilfillian's funky jam \"Here and Now\" boomed smooth, soulful tunes throughout my small apartment. The twang of the electric guitar played nicely with the thudding percussion but never overshadowed Gilfillian or the female backup vocals.    Bang & Olufsen software comes preinstalled on the Envy 13, with equalizer controls so you can adjust the bass, midrange and treble to your liking. But even out of the box, you'll enjoy great sound without having to bust out your headphones.  Battery Life  Get an Envy 13 with the 1080p non-touch display if battery life is important to you.   The FHD model endured for 11 hours and 11 minutes whereas the 4K model lasted only 4 hours and 36 minutes on our battery test, which involves continuous web browsing over Wi-Fi at 150 nits of brightness.   MORE: Laptops with Best Battery Life - Longest Lasting Laptop Batteries  Competing laptops like the ZenBook S UX391UA (7:05), Surface Laptop 2 (9:22) and Notebook 9 Pro (8:53) outstayed the 4K Envy 13 but powered down long before the 1080p version.  Webcam  The 720p webcam on the Envy 13 is nothing to write home about. A selfie I snapped in my dimly lit room was covered in a haze of visual noise. My beard and hair were unkempt blobs, while my eyes looked like they were drawn on by a pointillist painter. If there's one positive, it's that the lens captures natural colors and even extracted the different shades of gray in my T-shirt.   On the right edge of the Envy 13 is a physical kill switch that cuts the power to the webcam so you can feel reassured that nobody is snooping on you.   Heat  Leave the lapdesk at home - you don't have to worry about the Envy 13 overheating.    After I played a 15-minute, full-HD video in full screen, the touchpad on the HP Envy 13 with a Core i7 CPU rose to only 83 degrees Fahrenheit while the keyboard (87 degrees) and underside (90 degrees) also remained well below our 95-degree comfort threshold. Even the toastiest part of the machine, the lower-left edge on the underside, topped out at 94 degrees.   Software and Warranty  It's a shame that a laptop with such beautiful hardware ships with such ugly software. Pre-installed on this machine are entirely too many programs that could either be packaged together or omitted altogether.   HP provides an app called Audio Switch, which simply lets you switch your audio input/output between the internal speakers and headphones. As the same implies, HP's Command Center is where you can get information about your Envy 13 but also switch the thermal profiles between comfort and performance. Along with support documentation, HP also bundles in a setup program called JumpStart, a program for connecting printers and a redundant system-info app called Event Utility.   Also installed on the Envy 13's Windows 10 Home OS are several Microsoft apps, including Simple Solitaire, Candy Crush Friends and Your Phone. Other third-party apps include Booking.com, Netflix and McAfee Security.   HP ships the Envy 13 with a one-year warranty. See how HP did on our Tech Support Showdown and Best and Worst Brands ranking.   Bottom Line  The Envy 13 has cemented its standing as the ultimate laptop for college students or travelers. Along with 11-plus hours of battery life (on the FHD model), the Envy 13 has a sleek, ultraportable chassis, fast performance, and powerful speakers. Best of all, the Envy 13 starts at a reasonable $799, which is hundreds less than the competition. In many ways, the Envy 13 is what we wanted the new MacBook Air to be.   The new HP Envy 13 is everything I was hoping the new MacBook Air would be: fast, attractive and affordable.  Just be sure to buy the right model. We strongly recommend the 1080p version over the 4K model because it lasts several hours longer on a charge and costs less. In fact, if we were reviewing the 4K model separately, we'd only give it a 3.5 rating. You should also consider the Envy 13 with a 10th Gen CPU, although we haven't gotten the chance to review it yet.   If you absolutely need a high-res display, the 4K Envy 13 is one of many good options. We also recommend the Samsung Notebook 9 Pro, which has a similarly premium design but much better battery life than the 4K Envy. The Microsoft Surface Laptop 2 is another recommended alternative, though you might want to wait a few months for the rumored Surface Laptop 3.   Overall, the HP Envy 13 is a fantastic laptop that checks all the right boxes --- as long as you buy the 1080p model.   Credit: Laptop Mag  HP Envy 13 (2019) Specs BluetoothBluetooth 5.0 BrandHP CPUIntel Core i7-8565U Card SlotsmicroSD Company Websitehttps://www8.hp.com/us/en/home.html Display Size13.3 Graphics CardNvidia GeForce MX250 Hard Drive Size512GB Hard Drive TypePCIe NVMe M.2 Highest Available Resolution3840 x 2160 Native Resolution3840 x 2160 Operating SystemWindows 10 Home Ports (excluding USB)USB 3.1 with Type-C, USB 3.1 Always-On, USB 3.1, Headphone/Mic, microSD RAM16GB RAM Upgradable to16GB Size12.1 x 8.3 x .57 inches Touchpad Size4.3 x 2.2 inches USB Ports3 Video Memory2GB Warranty/Supportone-year warranty. Weight2.8 pounds Wi-Fi802.11ac Wi-Fi ModelIntel Wireless-AC 9560 ",
                    "id": "doc3"
                }
            ],
            "language": "en"
        }
        request = build_get_answers_from_text_request(
            json=json_content
        )
        response = await client.send_request(request)
        assert response.status_code == 200

        output = response.json()
        assert output.get('answers')
        for answer in output['answers']:
            assert answer.get('answer')
            assert answer.get('confidenceScore')
            assert answer.get('id')
            assert answer.get('offset')
            assert answer.get('length')
            assert answer.get('answerSpan')
            assert answer['answerSpan'].get('text')
            assert answer['answerSpan'].get('confidenceScore')
            assert answer['answerSpan'].get('offset') is not None
            assert answer['answerSpan'].get('length')

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text(self, qna_account, qna_key):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        params = AnswersFromTextOptions(
            question="What is the meaning of life?",
            text_documents=[
                TextDocument(
                    text="abc Graphics  Surprise, surprise -- our 4K  ",
                    id="doc1"
                ),
                TextDocument(
                    text="e graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on  ",
                    id="doc2"
                ),
                TextDocument(
                    text="Graphics  Surprise, surprise -- our 4K Envy 13 came with a discrete graphics card. While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   The MX250-equipped Envy 13 scored a 116,575 on the Ice Storm Unlimited benchmark while the base model scored a 82,270. Upgrading to the discrete graphics gives the Envy 13 better performance than the Notebook 9 Pro (61,662; UHD 620), Surface Laptop 2 (71,647; UHD 620) and the premium laptop average (86,937).   While the Nvidia GeForce MX250 GPU isn't meant for demanding gaming, it is a step up from integrated graphics as proven by comparing it to the UHD 620 GPU in the FHD model.   We played the racing game Dirt 3 at 92 frames per second on the MX250 model, which is well above our 30-fps playability, the category average (69 fps) and what the Surface Laptop 2 (82 fps) achieved. The ZenBook S UX391UA (45 fps) fell flat on this real-world test but ran better than the base model Envy 13 (31 fps).  Audio  I had a good ol' time groovin' to the sound of the Envy 13's crisp speakers. HP went all out with the Envy, placing dual speakers on the underside of the chassis along with a third, top-firing driver above the keyboard. Devon Gilfillian's funky jam \"Here and Now\" boomed smooth, soulful tunes throughout my small apartment. The twang of the electric guitar played nicely with the thudding percussion but never overshadowed Gilfillian or the female backup vocals.    Bang & Olufsen software comes preinstalled on the Envy 13, with equalizer controls so you can adjust the bass, midrange and treble to your liking. But even out of the box, you'll enjoy great sound without having to bust out your headphones.  Battery Life  Get an Envy 13 with the 1080p non-touch display if battery life is important to you.   The FHD model endured for 11 hours and 11 minutes whereas the 4K model lasted only 4 hours and 36 minutes on our battery test, which involves continuous web browsing over Wi-Fi at 150 nits of brightness.   MORE: Laptops with Best Battery Life - Longest Lasting Laptop Batteries  Competing laptops like the ZenBook S UX391UA (7:05), Surface Laptop 2 (9:22) and Notebook 9 Pro (8:53) outstayed the 4K Envy 13 but powered down long before the 1080p version.  Webcam  The 720p webcam on the Envy 13 is nothing to write home about. A selfie I snapped in my dimly lit room was covered in a haze of visual noise. My beard and hair were unkempt blobs, while my eyes looked like they were drawn on by a pointillist painter. If there's one positive, it's that the lens captures natural colors and even extracted the different shades of gray in my T-shirt.   On the right edge of the Envy 13 is a physical kill switch that cuts the power to the webcam so you can feel reassured that nobody is snooping on you.   Heat  Leave the lapdesk at home - you don't have to worry about the Envy 13 overheating.    After I played a 15-minute, full-HD video in full screen, the touchpad on the HP Envy 13 with a Core i7 CPU rose to only 83 degrees Fahrenheit while the keyboard (87 degrees) and underside (90 degrees) also remained well below our 95-degree comfort threshold. Even the toastiest part of the machine, the lower-left edge on the underside, topped out at 94 degrees.   Software and Warranty  It's a shame that a laptop with such beautiful hardware ships with such ugly software. Pre-installed on this machine are entirely too many programs that could either be packaged together or omitted altogether.   HP provides an app called Audio Switch, which simply lets you switch your audio input/output between the internal speakers and headphones. As the same implies, HP's Command Center is where you can get information about your Envy 13 but also switch the thermal profiles between comfort and performance. Along with support documentation, HP also bundles in a setup program called JumpStart, a program for connecting printers and a redundant system-info app called Event Utility.   Also installed on the Envy 13's Windows 10 Home OS are several Microsoft apps, including Simple Solitaire, Candy Crush Friends and Your Phone. Other third-party apps include Booking.com, Netflix and McAfee Security.   HP ships the Envy 13 with a one-year warranty. See how HP did on our Tech Support Showdown and Best and Worst Brands ranking.   Bottom Line  The Envy 13 has cemented its standing as the ultimate laptop for college students or travelers. Along with 11-plus hours of battery life (on the FHD model), the Envy 13 has a sleek, ultraportable chassis, fast performance, and powerful speakers. Best of all, the Envy 13 starts at a reasonable $799, which is hundreds less than the competition. In many ways, the Envy 13 is what we wanted the new MacBook Air to be.   The new HP Envy 13 is everything I was hoping the new MacBook Air would be: fast, attractive and affordable.  Just be sure to buy the right model. We strongly recommend the 1080p version over the 4K model because it lasts several hours longer on a charge and costs less. In fact, if we were reviewing the 4K model separately, we'd only give it a 3.5 rating. You should also consider the Envy 13 with a 10th Gen CPU, although we haven't gotten the chance to review it yet.   If you absolutely need a high-res display, the 4K Envy 13 is one of many good options. We also recommend the Samsung Notebook 9 Pro, which has a similarly premium design but much better battery life than the 4K Envy. The Microsoft Surface Laptop 2 is another recommended alternative, though you might want to wait a few months for the rumored Surface Laptop 3.   Overall, the HP Envy 13 is a fantastic laptop that checks all the right boxes --- as long as you buy the 1080p model.   Credit: Laptop Mag  HP Envy 13 (2019) Specs BluetoothBluetooth 5.0 BrandHP CPUIntel Core i7-8565U Card SlotsmicroSD Company Websitehttps://www8.hp.com/us/en/home.html Display Size13.3 Graphics CardNvidia GeForce MX250 Hard Drive Size512GB Hard Drive TypePCIe NVMe M.2 Highest Available Resolution3840 x 2160 Native Resolution3840 x 2160 Operating SystemWindows 10 Home Ports (excluding USB)USB 3.1 with Type-C, USB 3.1 Always-On, USB 3.1, Headphone/Mic, microSD RAM16GB RAM Upgradable to16GB Size12.1 x 8.3 x .57 inches Touchpad Size4.3 x 2.2 inches USB Ports3 Video Memory2GB Warranty/Supportone-year warranty. Weight2.8 pounds Wi-Fi802.11ac Wi-Fi ModelIntel Wireless-AC 9560 ",
                    id="doc3"
                )
            ],
            language="en"
        )

        output = await client.get_answers_from_text(params)
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence
            assert answer.id
            assert answer.offset
            assert answer.length
            assert answer.short_answer
            assert answer.short_answer.text
            assert answer.short_answer.confidence
            assert answer.short_answer.offset is not None
            assert answer.short_answer.length

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text_with_dictparams(self, qna_account, qna_key):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        params = {
            "question": "How long it takes to charge surface?",
            "records": [
                {
                    "text": "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                            "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                    "id": "1"
                },
                {
                    "text": "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "+
                            "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
                    "id": "2"
                }
            ],
            "language": "en"
        }

        async with client:
            output = await client.get_answers_from_text(params)
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text_with_str_records(self, qna_account, qna_key):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        params = {
            "question": "How long it takes to charge surface?",
            "records": [
                "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "+
                "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
            ],
            "language": "en"
        }

        async with client:
            output = await client.get_answers_from_text(params)
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text_overload(self, qna_account, qna_key):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))

        async with client:
            with pytest.raises(TypeError):
                await client.get_answers_from_text(
                    question="How long it takes to charge surface?",
                    text_documents=[
                        "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                        "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                        {
                            "text": "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "+
                                    "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
                            "id": "2"
                        }
                    ]
                )
            output = await client.get_answers_from_text(
                question="How long it takes to charge surface?",
                text_documents=[
                    "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                    "It can take longer if you’re using your Surface for power-intensive activities like gaming or video streaming while you’re charging it.",
                    "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. "+
                    "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
                ]
            )
            assert len(output.answers) == 3
            confident_answers = [a for a in output.answers if a.confidence > 0.9]
            assert len(confident_answers) == 2
            assert confident_answers[0].short_answer.text == "two to four hours"

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_query_text_overload_positional_and_kwarg(self):
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                await client.get_answers_from_text("positional_one", "positional_two")
            with pytest.raises(TypeError):
                await client.get_answers_from_text("positional_options_bag", options="options bag by name")
