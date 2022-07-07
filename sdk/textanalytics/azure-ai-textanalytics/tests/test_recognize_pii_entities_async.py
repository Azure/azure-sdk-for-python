# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
import platform
import functools
import json
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest
from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
    PiiEntityDomain,
    PiiEntityCategory
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
# the first one
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestRecognizePIIEntities(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_no_single_input(self, client):
        with pytest.raises(TypeError):
            response = await client.recognize_pii_entities("hello world")

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_dict(self, client):

        docs = [{"id": "1", "text": "My SSN is 859-98-0987."},
                {"id": "2", "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = await client.recognize_pii_entities(docs, show_stats=True)
        assert response[0].entities[0].text == "859-98-0987"
        assert response[0].entities[0].category == "USSocialSecurityNumber"
        assert response[1].entities[0].text == "111000025"
        # assert response[1].entities[0].category == "ABA Routing Number"  # Service is currently returning PhoneNumber here

        # commenting out brazil cpf, currently service is not returning it
        # assert response[2].entities[0].text == "998.214.865-68"
        # assert response[2].entities[0].category == "Brazil CPF Number"
        for doc in response:
            assert doc.id is not None
            assert doc.statistics is not None
            for entity in doc.entities:
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_text_document_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="My SSN is 859-98-0987."),
            TextDocumentInput(id="2", text="Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."),
            TextDocumentInput(id="3", text="Is 998.214.865-68 your Brazilian CPF number?")
        ]

        response = await client.recognize_pii_entities(docs, show_stats=True)
        assert response[0].entities[0].text == "859-98-0987"
        assert response[0].entities[0].category == "USSocialSecurityNumber"
        assert response[1].entities[0].text == "111000025"
        # assert response[1].entities[0].category == "ABA Routing Number"  # Service is currently returning PhoneNumber here
        # commenting out brazil cpf, currently service is not returning it
        # assert response[2].entities[0].text == "998.214.865-68"
        # assert response[2].entities[0].category == "Brazil CPF Number"
        for doc in response:
            assert doc.id is not None
            assert doc.statistics is not None
            for entity in doc.entities:
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_only_string(self, client):
        docs = [
            "My SSN is 859-98-0987.",
            "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
            "Is 998.214.865-68 your Brazilian CPF number?",
            ""
        ]

        response = await client.recognize_pii_entities(docs, show_stats=True)
        assert response[0].entities[0].text == "859-98-0987"
        assert response[0].entities[0].category == "USSocialSecurityNumber"
        assert response[1].entities[0].text == "111000025"
        # assert response[1].entities[0].category == "ABA Routing Number"  # Service is currently returning PhoneNumber here

        # commenting out brazil cpf, currently service is not returning it
        # assert response[2].entities[0].text == "998.214.865-68"
        # assert response[2].entities[0].category == "Brazil CPF Number"
        assert response[3].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "notalanguage", "text": "hola"},
                {"id": "2", "text": ""},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = await client.recognize_pii_entities(docs)
        assert response[0].is_error
        assert response[1].is_error
        # assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_all_errors(self, client):
        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Hola"},
                {"id": "3", "language": "de", "text": ""}]

        response = await client.recognize_pii_entities(docs)
        assert response[0].is_error
        assert response[1].is_error
        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_too_many_documents(self, client):
        docs = ["One", "Two", "Three", "Four", "Five", "Six"]

        with pytest.raises(HttpResponseError) as excinfo:
            await client.recognize_pii_entities(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_output_same_order_as_input(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = await client.recognize_pii_entities(docs)

        for idx, doc in enumerate(response):
            assert str(idx + 1) == doc.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": ""})
    @recorded_by_proxy_async
    async def test_empty_credential_class(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_pii_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": "xxxxxxxxxxxx"})
    @recorded_by_proxy_async
    async def test_bad_credentials(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_pii_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with pytest.raises(TypeError):
            response = await client.recognize_pii_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            "You cannot mix string input with the above inputs"
        ]
        with pytest.raises(TypeError):
            response = await client.recognize_pii_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.recognize_pii_entities(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            assert resp.id == in_order[idx]

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_show_stats_and_model_version(self, client):
        def callback(response):
            assert response is not None
            assert response.model_version
            assert response.raw_response is not None
            assert response.statistics.document_count == 5
            assert response.statistics.transaction_count == 4
            assert response.statistics.valid_document_count == 4
            assert response.statistics.erroneous_document_count == 1

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.recognize_pii_entities(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_batch_size_over_limit(self, client):
        docs = ["hello world"] * 1050
        with pytest.raises(HttpResponseError):
            response = await client.recognize_pii_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = await client.recognize_pii_entities(docs, language="fr", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = await client.recognize_pii_entities(docs, language="", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_per_item_dont_use_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1


        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.recognize_pii_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_language_hint_and_obj_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = await client.recognize_pii_entities(docs, language="de", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="es"),
            TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="es"),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = await client.recognize_pii_entities(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 2
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 1


        docs = [{"id": "1", "language": "es", "text": "I will go to the park."},
                {"id": "2", "language": "es", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.recognize_pii_entities(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "es"})
    @recorded_by_proxy_async
    async def test_client_passed_default_language_hint(self, client):
        def callback(resp):
            language_str = "\"language\": \"es\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        def callback_2(resp):
            language_str = "\"language\": \"en\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.recognize_pii_entities(docs, raw_response_hook=callback)
        response = await client.recognize_pii_entities(docs, language="en", raw_response_hook=callback_2)
        response = await client.recognize_pii_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_method(self, client):
        response = await client.recognize_pii_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_docs(self, client):
        response = await client.recognize_pii_entities(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @recorded_by_proxy_async
    async def test_rotate_subscription_key(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        credential = AzureKeyCredential(textanalytics_test_api_key)
        client = TextAnalyticsClient(textanalytics_test_endpoint, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.recognize_pii_entities(docs)
        assert response is not None

        credential.update("xxx")  # Make authentication fail
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_pii_entities(docs)

        credential.update(textanalytics_test_api_key)  # Authenticate successfully again
        response = await client.recognize_pii_entities(docs)
        assert response is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_user_agent(self, client):
        def callback(resp):
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()) in \
                resp.http_request.headers["User-Agent"]

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.recognize_pii_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.recognize_pii_entities(docs)

        # Attributes on DocumentError
        assert response[0].is_error
        assert response[0].id == "1"
        assert response[0].error is not None

        # Result attribute not on DocumentError, custom error message
        try:
            entities = response[0].entities
        except AttributeError as custom_error:
            assert custom_error.args[0] == \
                '\'DocumentError\' object has no attribute \'entities\'. ' \
                'The service was unable to process this document:\nDocument Id: 1\nError: ' \
                'InvalidDocument - Document text is empty.\n'


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.recognize_pii_entities(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            entities = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            assert default_behavior.args[0] == '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = await client.recognize_pii_entities(docs, model_version="bad")
        except HttpResponseError as err:
            assert err.error.code == "ModelVersionIncorrect"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = await client.recognize_pii_entities(docs)
        assert doc_errors[0].error.code == "InvalidDocument"
        assert doc_errors[0].error.message is not None
        assert doc_errors[1].error.code == "UnsupportedLanguageCode"
        assert doc_errors[1].error.message is not None
        assert doc_errors[2].error.code == "InvalidDocument"
        assert doc_errors[2].error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_warnings(self, client):
        # No warnings actually returned for recognize_pii_entities. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = await client.recognize_pii_entities(docs)
        for doc in result:
            doc_warnings = doc.warnings
            assert len(doc_warnings) == 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            await client.recognize_pii_entities(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            await client.recognize_pii_entities(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.recognize_pii_entities(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = await client.recognize_pii_entities(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocument"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_batch_size_over_limit_error(self, client):
        # Batch size over limit
        docs = ["hello world"] * 1001
        try:
            response = await client.recognize_pii_entities(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocumentBatch"
            assert err.error.message is not None


    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = await client.recognize_pii_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_language_kwarg_english(self, client):
        def callback(response):
            language_str = "\"language\": \"en\""
            assert response.http_request.body.count(language_str) == 1
            assert response.model_version is not None
            assert response.statistics is not None

        res = await client.recognize_pii_entities(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="en",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_redacted_text(self, client):
        result = await client.recognize_pii_entities(["My SSN is 859-98-0987."])
        assert "My SSN is ***********." == result[0].redacted_text

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_phi_domain_filter(self, client):
        # without the domain filter, this should return two entities: Microsoft as an org,
        # and the phone number. With the domain filter, it should only return one.
        result = await client.recognize_pii_entities(
            ["I work at Microsoft and my phone number is 333-333-3333"],
            domain_filter=PiiEntityDomain.PROTECTED_HEALTH_INFORMATION
        )
        assert len(result[0].entities) == 2
        microsoft = list(filter(lambda x: x.text == "Microsoft", result[0].entities))[0]
        phone = list(filter(lambda x: x.text == "333-333-3333", result[0].entities))[0]
        assert phone.category == "PhoneNumber"
        assert microsoft.category == "Organization"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_categories_filter(self, client):
        result = await client.recognize_pii_entities(
            ["My name is Inigo Montoya, my SSN in 243-56-0987 and my phone number is 333-3333."],
        )

        # assert len(result[0].entities) == 3  FIXME service returning entity for "333-3333" and "333-3333."

        result = await client.recognize_pii_entities(
            ["My name is Inigo Montoya, my SSN in 243-56-0987 and my phone number is 333-3333."],
            categories_filter=[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]
        )

        assert len(result[0].entities) == 1
        entity = result[0].entities[0]
        assert entity.category == PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER.value

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_categories_filter_with_domain_filter(self, client):
        # Currently there seems to be no effective difference with or without the PHI domain filter.
        result = await client.recognize_pii_entities(
            ["My name is Inigo Montoya, my SSN in 243-56-0987 and my phone number is 333-3333."],
            categories_filter=[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER],
            domain_filter=PiiEntityDomain.PROTECTED_HEALTH_INFORMATION
        )

        assert len(result[0].entities) == 1
        entity = result[0].entities[0]
        assert entity.category == PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER.value

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "UnicodeCodePoint"

        res = await client.recognize_pii_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy_async
    async def test_default_string_index_type_UnicodeCodePoint_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "UnicodeCodePoint"

        res = await client.recognize_pii_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_explicit_set_string_index_type(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "TextElement_v8"

        res = await client.recognize_pii_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy_async
    async def test_explicit_set_string_index_type_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "TextElements_v8"

        res = await client.recognize_pii_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_disable_service_logs(self, client):
        def callback(resp):
            assert resp.http_request.query['loggingOptOut']
        await client.recognize_pii_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy_async
    async def test_disable_service_logs_body_param(self, client):
        def callback(resp):
            assert json.loads(resp.http_request.body)['parameters']['loggingOptOut']
        await client.recognize_pii_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    async def test_pii_entities_multiapi_validate_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            await client.recognize_pii_entities(
                documents=["Test"]
            )
        assert str(e.value) == "'recognize_pii_entities' is only available for API version v3.1 and up."
