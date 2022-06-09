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
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

class TestRecognizeEntities(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_no_single_input(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(TypeError):
            response = client.recognize_entities("hello world")

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_all_successful_passing_dict(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975."},
                {"id": "3", "language": "de", "text": "Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet."}]

        response = client.recognize_entities(docs, model_version="2020-02-01", show_stats=True)
        for doc in response:
            # assert len(doc.entities) == 4 commenting out because of service error
            assert doc.id is not None
            assert doc.statistics is not None
            for entity in doc.entities:
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_all_successful_passing_text_document_input(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.", language="es"),
            TextDocumentInput(id="3", text="Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.", language="de")
        ]

        response = client.recognize_entities(docs, model_version="2020-02-01")
        for doc in response:
            # assert len(doc.entities) == 4 commenting out because of service error
            for entity in doc.entities:
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_passing_only_string(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.",
            "Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.",
            "Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.",
            ""
        ]

        response = client.recognize_entities(docs)
        assert len(response[0].entities) == 4
        assert response[3].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_input_with_some_errors(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."},
                {"id": "2", "language": "Spanish", "text": "Hola"},
                {"id": "3", "language": "de", "text": ""}]

        response = client.recognize_entities(docs)
        assert not response[0].is_error
        assert response[1].is_error
        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_input_with_all_errors(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "Spanish", "text": "Hola"},
                {"id": "3", "language": "de", "text": ""}]

        response = client.recognize_entities(docs)
        assert response[0].is_error
        assert response[1].is_error
        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_too_many_documents(self, **kwargs):
        client = kwargs.pop("client")
        docs = ["One", "Two", "Three", "Four", "Five", "Six"]

        with pytest.raises(HttpResponseError) as excinfo:
            client.recognize_entities(docs)
        assert excinfo.value.status_code == 400
        assert excinfo.value.error.code == "InvalidDocumentBatch"
        assert "Batch request contains too many records" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_output_same_order_as_input(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = client.recognize_entities(docs)

        for idx, doc in enumerate(response):
            assert str(idx + 1) == doc.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": ""})
    @recorded_by_proxy
    def test_empty_credential_class(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ClientAuthenticationError):
            response = client.recognize_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": "xxxxxxxxxxxx"})
    @recorded_by_proxy
    def test_bad_credentials(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ClientAuthenticationError):
            response = client.recognize_entities(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_bad_document_input(self, **kwargs):
        client = kwargs.pop("client")
        docs = "This is the wrong type"

        with pytest.raises(TypeError):
            response = client.recognize_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_mixing_inputs(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            "You cannot mix string input with the above inputs"
        ]
        with pytest.raises(TypeError):
            response = client.recognize_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_out_of_order_ids(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.recognize_entities(docs)
        in_order = ["56", "0", "22", "19", "1"]
        for idx, resp in enumerate(response):
            assert resp.id == in_order[idx]

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_show_stats_and_model_version(self, **kwargs):
        client = kwargs.pop("client")
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

        response = client.recognize_entities(
            docs,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_batch_size_over_limit(self, **kwargs):
        client = kwargs.pop("client")
        docs = ["hello world"] * 1050
        with pytest.raises(HttpResponseError):
            response = client.recognize_entities(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            language_str = "\"language\": \"fr\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = client.recognize_entities(docs, language="fr", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_dont_use_language_hint(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            language_str = "\"language\": \"\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = client.recognize_entities(docs, language="", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_per_item_dont_use_language_hint(self, **kwargs):
        client = kwargs.pop("client")
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

        response = client.recognize_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_obj_input(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            assert language == 3

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = client.recognize_entities(docs, language="de", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, **kwargs):
        client = kwargs.pop("client")
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

        response = client.recognize_entities(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, **kwargs):
        client = kwargs.pop("client")
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

        response = client.recognize_entities(docs, language="en", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_language": "es"})
    @recorded_by_proxy
    def test_client_passed_default_language_hint(self, **kwargs):
        client = kwargs.pop("client")
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

        response = client.recognize_entities(docs, raw_response_hook=callback)
        response = client.recognize_entities(docs, language="en", raw_response_hook=callback_2)
        response = client.recognize_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_method(self, **kwargs):
        client = kwargs.pop("client")
        response = client.recognize_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage"
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_docs(self, **kwargs):
        client = kwargs.pop("client")
        response = client.recognize_entities(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]
        )
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @recorded_by_proxy
    def test_rotate_subscription_key(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        credential = AzureKeyCredential(textanalytics_test_api_key)
        client = TextAnalyticsClient(textanalytics_test_endpoint, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.recognize_entities(docs)
        assert response is not None

        credential.update("xxx")  # Make authentication fail
        with pytest.raises(ClientAuthenticationError):
            response = client.recognize_entities(docs)

        credential.update(textanalytics_test_api_key)  # Authenticate successfully again
        response = client.recognize_entities(docs)
        assert response is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_user_agent(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()) in \
                resp.http_request.headers["User-Agent"]

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.recognize_entities(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_attribute_error_no_result_attribute(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "text": ""}]
        response = client.recognize_entities(docs)

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
    @recorded_by_proxy
    def test_document_attribute_error_nonexistent_attribute(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "text": ""}]
        response = client.recognize_entities(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            entities = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            assert default_behavior.args[0] == '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_bad_model_version_error(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = client.recognize_entities(docs, model_version="bad")
        except HttpResponseError as err:
            assert err.error.code == "ModelVersionIncorrect"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_errors(self, **kwargs):
        client = kwargs.pop("client")
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        doc_errors = client.recognize_entities(docs)
        assert doc_errors[0].error.code == "InvalidDocument"
        assert doc_errors[0].error.message is not None
        assert doc_errors[1].error.code == "UnsupportedLanguageCode"
        assert doc_errors[1].error.message is not None
        assert doc_errors[2].error.code == "InvalidDocument"
        assert doc_errors[2].error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_warnings(self, **kwargs):
        client = kwargs.pop("client")
        # No warnings actually returned for recognize_entities. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = client.recognize_entities(docs)
        for doc in result:
            doc_warnings = doc.warnings
            assert len(doc_warnings) == 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_not_passing_list_for_docs(self, **kwargs):
        client = kwargs.pop("client")
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            client.recognize_entities(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_missing_input_records_error(self, **kwargs):
        client = kwargs.pop("client")
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.recognize_entities(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_passing_none_docs(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as excinfo:
            client.recognize_entities(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_duplicate_ids_error(self, **kwargs):
        client = kwargs.pop("client")
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.recognize_entities(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocument"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_batch_size_over_limit_error(self, **kwargs):
        client = kwargs.pop("client")
        # Batch size over limit
        docs = ["hello world"] * 1001
        try:
            response = client.recognize_entities(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocumentBatch"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_language_kwarg_spanish(self, **kwargs):
        client = kwargs.pop("client")
        def callback(response):
            language_str = "\"language\": \"es\""
            assert response.http_request.body.count(language_str) == 1
            assert response.model_version is not None
            assert response.statistics is not None

        res = client.recognize_entities(
            documents=["Bill Gates is the CEO of Microsoft."],
            model_version="latest",
            show_stats=True,
            language="es",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_pass_cls(self, **kwargs):
        client = kwargs.pop("client")
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.recognize_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_offset(self, **kwargs):
        client = kwargs.pop("client")
        result = client.recognize_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        assert entities[0].offset == 0

        assert entities[1].offset == 25

        assert entities[2].offset == 40

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    @recorded_by_proxy
    def test_no_offset_v3_categorized_entities(self, **kwargs):
        client = kwargs.pop("client")
        result = client.recognize_entities(["Microsoft was founded by Bill Gates and Paul Allen"])
        entities = result[0].entities

        assert entities[0].offset is None
        assert entities[1].offset is None
        assert entities[2].offset is None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_default_string_index_type_is_UnicodeCodePoint(self, **kwargs):
        client = kwargs.pop("client")
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "UnicodeCodePoint"

        res = client.recognize_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_default_string_index_type_UnicodeCodePoint_body_param(self, **kwargs):
        client = kwargs.pop("client")
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "UnicodeCodePoint"

        res = client.recognize_entities(
            documents=["Hello world"],
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_explicit_set_string_index_type(self, **kwargs):
        client = kwargs.pop("client")
        def callback(response):
            assert response.http_request.query["stringIndexType"] == "TextElement_v8"

        res = client.recognize_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_explicit_set_string_index_type_body_param(self, **kwargs):
        client = kwargs.pop("client")
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "TextElements_v8"

        res = client.recognize_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_disable_service_logs(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            assert resp.http_request.query['loggingOptOut']
        client.recognize_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_05_01})
    @recorded_by_proxy
    def test_disable_service_logs_body_param(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            assert json.loads(resp.http_request.body)['parameters']['loggingOptOut']
        client.recognize_entities(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    def test_entities_multiapi_validate_args_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            res = client.recognize_entities(["I'm tired"], string_index_type="UnicodeCodePoint")
        assert str(e.value) == "'string_index_type' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = client.recognize_entities(["I'm tired"], disable_service_logs=True)
        assert str(e.value) == "'disable_service_logs' is only available for API version v3.1 and up.\n"

        with pytest.raises(ValueError) as e:
            res = client.recognize_entities(["I'm tired"], string_index_type="UnicodeCodePoint", disable_service_logs=True)
        assert str(e.value) == "'string_index_type' is only available for API version v3.1 and up.\n'disable_service_logs' is only available for API version v3.1 and up.\n"
