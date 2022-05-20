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
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    VERSION,
    DetectLanguageInput,
    TextDocumentInput,
    TextAnalyticsApiVersion,
)

from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import TextAnalyticsTest

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestRecognizeLinkedEntities(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_no_single_input(self, client):
        with pytest.raises(TypeError):
            response = await client.recognize_linked_entities("hello world")

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_dict(self, client):

        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = await client.recognize_linked_entities(docs, show_stats=True)
        for doc in response:
            assert len(doc.entities) == 3
            assert doc.id is not None
            assert doc.statistics is not None
            for entity in doc.entities:
                assert entity.name is not None
                assert entity.language is not None
                assert entity.data_source_entity_id is not None
                assert entity.url is not None
                assert entity.data_source is not None
                assert entity.matches is not None
                for match in entity.matches:
                    assert match.offset is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_text_document_input(self, client):

        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen")
        ]

        response = await client.recognize_linked_entities(docs)
        for doc in response:
            assert len(doc.entities) == 3
            for entity in doc.entities:
                assert entity.name is not None
                assert entity.language is not None
                assert entity.data_source_entity_id is not None
                assert entity.url is not None
                assert entity.data_source is not None
                assert entity.matches is not None
                for match in entity.matches:
                    assert match.offset is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_only_string(self, client):

        docs = [
            "Microsoft was founded by Bill Gates and Paul Allen",
            "Microsoft fue fundado por Bill Gates y Paul Allen",
            ""
        ]

        response = await client.recognize_linked_entities(docs)
        assert len(response[0].entities) == 3
        assert len(response[1].entities) == 3
        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_some_errors(self, client):

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = await client.recognize_linked_entities(docs)
        assert response[0].is_error
        assert not response[1].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_all_errors(self, client):

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = await client.recognize_linked_entities(docs)
        assert response[0].is_error
        assert response[1].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_too_many_documents(self, client):
        docs = ["One", "Two", "Three", "Four", "Five", "Six"]

        with pytest.raises(HttpResponseError) as excinfo:
            await client.recognize_linked_entities(docs)
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

        response = await client.recognize_linked_entities(docs)

        for idx, doc in enumerate(response):
            assert str(idx + 1) == doc.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": ""})
    @recorded_by_proxy_async
    async def test_empty_credential_class(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_linked_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": "xxxxxxxxxxxx"})
    @recorded_by_proxy_async
    async def test_bad_credentials(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_linked_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_document_input(self, client):

        docs = "This is the wrong type"

        with pytest.raises(TypeError):
            response = await client.recognize_linked_entities(docs)

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
            response = await client.recognize_linked_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_out_of_order_ids(self, client):

        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.recognize_linked_entities(docs)
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

        response = await client.recognize_linked_entities(
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
            response = await client.recognize_linked_entities(docs)

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

        response = await client.recognize_linked_entities(docs, language="fr", raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, language="", raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, language="de", raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, language="en", raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, language="en", raw_response_hook=callback)

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

        response = await client.recognize_linked_entities(docs, raw_response_hook=callback)
        response = await client.recognize_linked_entities(docs, language="en", raw_response_hook=callback_2)
        response = await client.recognize_linked_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_method(self, client):
        response = await client.recognize_linked_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_docs(self, client):
        response = await client.recognize_linked_entities(
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

        response = await client.recognize_linked_entities(docs)
        assert response is not None

        credential.update("xxx")  # Make authentication fail
        with pytest.raises(ClientAuthenticationError):
            response = await client.recognize_linked_entities(docs)

        credential.update(textanalytics_test_api_key)  # Authenticate successfully again
        response = await client.recognize_linked_entities(docs)
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

        response = await client.recognize_linked_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_attribute_error_no_result_attribute(self, client):

        docs = [{"id": "1", "text": ""}]
        response = await client.recognize_linked_entities(docs)

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
        response = await client.recognize_linked_entities(docs)

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
            result = await client.recognize_linked_entities(docs, model_version="bad")
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

        doc_errors = await client.recognize_linked_entities(docs)
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
        # No warnings actually returned for recognize_linked_entities. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = await client.recognize_linked_entities(docs)
        for doc in result:
            doc_warnings = doc.warnings
            assert len(doc_warnings) == 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            await client.recognize_linked_entities(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            await client.recognize_linked_entities(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.recognize_linked_entities(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = await client.recognize_linked_entities(docs)
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
            response = await client.recognize_linked_entities(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocumentBatch"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_language_kwarg_spanish(self, client):

        def callback(response):
            language_str = "\"language\": \"es\""
            assert response.http_request.body.count(language_str) == 1
            assert response.model_version is not None
            assert response.statistics is not None

        res = await client.recognize_linked_entities(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = await client.recognize_linked_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_offset(self, client):
        result = await client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        # the entities are being returned in a non-sequential order by the service
        microsoft_entity = [entity for entity in entities if entity.name == "Microsoft"][0]
        bill_gates_entity = [entity for entity in entities if entity.name == "Bill Gates"][0]
        paul_allen_entity = [entity for entity in entities if entity.name == "Paul Allen"][0]

        assert microsoft_entity.matches[0].offset == 0

        assert bill_gates_entity.matches[0].offset == 25

        assert paul_allen_entity.matches[0].offset == 40

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    @recorded_by_proxy_async
    async def test_no_offset_v3_linked_entity_match(self, client):
        result = await client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        assert entities[0].matches[0].offset is None
        assert entities[1].matches[0].offset is None
        assert entities[2].matches[0].offset is None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    @recorded_by_proxy_async
    async def test_string_index_type_not_fail_v3(self, client):
        # make sure that the addition of the string_index_type kwarg for v3.1-preview doesn't
        # cause v3.0 calls to fail
        await client.recognize_linked_entities(["please don't fail"])

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bing_id(self, client):
        result = await client.recognize_linked_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        for doc in result:
            for entity in doc.entities:
                assert entity.bing_entity_search_api_id  # this checks if it's None and if it's empty

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "UnicodeCodePoint"

        res = await client.recognize_linked_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_04_01_PREVIEW})
    @recorded_by_proxy_async
    async def test_default_string_index_type_UnicodeCodePoint_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "UnicodeCodePoint"

        res = await client.recognize_linked_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_explicit_set_string_index_type(self, client):
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "TextElement_v8"

        res = await client.recognize_linked_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_04_01_PREVIEW})
    @recorded_by_proxy_async
    async def test_explicit_set_string_index_type_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "TextElements_v8"

        res = await client.recognize_linked_entities(
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
        await client.recognize_linked_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_04_01_PREVIEW})
    @recorded_by_proxy_async
    async def test_disable_service_logs_body_param(self, client):
        def callback(resp):
            assert json.loads(resp.http_request.body)['parameters']['loggingOptOut']

        await client.recognize_linked_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    async def test_linked_entities_multiapi_validate_args_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            res = await client.recognize_linked_entities(["I'm tired"], string_index_type="UnicodeCodePoint")
        assert str(e.value) == "'string_index_type' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = await client.recognize_linked_entities(["I'm tired"], disable_service_logs=True)
        assert str(e.value) == "'disable_service_logs' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = await client.recognize_linked_entities(["I'm tired"], string_index_type="UnicodeCodePoint",
                                                   disable_service_logs=True)
        assert str(
            e.value) == "'string_index_type' is only available for API version v3.1 and up.\n'disable_service_logs' is only available for API version v3.1 and up.\n"
