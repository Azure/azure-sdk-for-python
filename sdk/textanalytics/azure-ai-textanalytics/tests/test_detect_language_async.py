# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import platform
import functools

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    VERSION,
    DetectLanguageInput,
    DetectLanguageInput,
    TextAnalyticsApiVersion,
)

from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import TextAnalyticsTest

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestDetectLanguage(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_no_single_input(self, client):
        with pytest.raises(TypeError):
            response = await client.detect_language("hello world")

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_dict(self, client):
        docs = [{"id": "1", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": "猫は幸せ"},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = await client.detect_language(docs, show_stats=True)

        assert response[0].primary_language.name == "English"
        # assert response[1].primary_language.name == "Spanish"  # https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/10363878
        assert response[2].primary_language.name == "Japanese"
        assert response[3].primary_language.name == "German"
        assert response[0].primary_language.iso6391_name == "en"
        # assert response[1].primary_language.iso6391_name == "es" # https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/10363878
        assert response[2].primary_language.iso6391_name == "ja"
        assert response[3].primary_language.iso6391_name == "de"

        for doc in response:
            assert doc.id is not None
            assert doc.statistics is not None
            assert doc.primary_language.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_all_successful_passing_text_document_input(self, client):
        docs = [
            DetectLanguageInput(id="1", text="I should take my cat to the veterinarian"),
            DetectLanguageInput(id="2", text="Este es un document escrito en Español."),
            DetectLanguageInput(id="3", text="猫は幸せ"),
            DetectLanguageInput(id="4", text="Fahrt nach Stuttgart und dann zum Hotel zu Fu.")
        ]

        response = await client.detect_language(docs)

        assert response[0].primary_language.name == "English"
        # assert response[1].primary_language.name == "Spanish"  # https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/10363878
        assert response[2].primary_language.name == "Japanese"
        assert response[3].primary_language.name == "German"
        assert response[0].primary_language.iso6391_name == "en"
        # assert response[1].primary_language.iso6391_name == "es" # https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/10363878
        assert response[2].primary_language.iso6391_name == "ja"
        assert response[3].primary_language.iso6391_name == "de"

        for doc in response:
            assert doc.primary_language.confidence_score is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_only_string(self, client):
        docs = [
            "I should take my cat to the veterinarian.",
            "Este es un document escrito en Español.",
            "猫は幸せ",
            "Fahrt nach Stuttgart und dann zum Hotel zu Fu.",
            ""
        ]

        response = await client.detect_language(docs)
        assert response[0].primary_language.name == "English"
        # assert response[1].primary_language.name == "Spanish"  # https://msazure.visualstudio.com/Cognitive%20Services/_workitems/edit/10363878
        assert response[2].primary_language.name == "Japanese"
        assert response[3].primary_language.name == "German"
        assert response[4].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "country_hint": "United States", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": ""},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = await client.detect_language(docs)

        assert response[0].is_error
        assert not response[1].is_error
        assert response[2].is_error
        assert not response[3].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_all_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "text": ""},
                {"id": "3", "text": ""},
                {"id": "4", "text": text}]

        response = await client.detect_language(docs)

        for resp in response:
            assert resp.is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_output_same_order_as_input(self, client):
        docs = [
            DetectLanguageInput(id="1", text="one"),
            DetectLanguageInput(id="2", text="two"),
            DetectLanguageInput(id="3", text="three"),
            DetectLanguageInput(id="4", text="four"),
            DetectLanguageInput(id="5", text="five")
        ]

        response = await client.detect_language(docs)

        for idx, doc in enumerate(response):
            assert str(idx + 1) == doc.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": ""})
    @recorded_by_proxy_async
    async def test_empty_credential_class(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.detect_language(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"textanalytics_test_api_key": "xxxxxxxxxxxx"})
    @recorded_by_proxy_async
    async def test_bad_credentials(self, client):
        with pytest.raises(ClientAuthenticationError):
            response = await client.detect_language(
                ["This is written in English."]
            )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with pytest.raises(TypeError):
            response = await client.detect_language(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            DetectLanguageInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            "You cannot mix string input with the above documents"
        ]
        with pytest.raises(TypeError):
            response = await client.detect_language(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_out_of_order_ids(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = await client.detect_language(docs)
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

        response = await client.detect_language(
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
            response = await client.detect_language(docs)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_country_hint(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = await client.detect_language(docs, country_hint="CA", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_dont_use_country_hint(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        docs = [
            "This was the best day of my life.",
            "I did not like the hotel we stayed at. It was too expensive.",
            "The restaurant was not as good as I hoped."
        ]

        response = await client.detect_language(docs, country_hint="", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_per_item_dont_use_country_hint(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"\""
            country = resp.http_request.body.count(country_str)
            assert country == 2
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            assert country == 1


        docs = [{"id": "1", "country_hint": "", "text": "I will go to the park."},
                {"id": "2", "country_hint": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_country_hint_and_obj_input(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        docs = [
            DetectLanguageInput(id="1", text="I should take my cat to the veterinarian."),
            DetectLanguageInput(id="2", text="Este es un document escrito en Español."),
            DetectLanguageInput(id="3", text="猫は幸せ"),
        ]

        response = await client.detect_language(docs, country_hint="CA", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_country_hint_and_dict_input(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs, country_hint="CA", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_country_hint_and_obj_per_item_hints(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 2
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            assert country == 1

        docs = [
            DetectLanguageInput(id="1", text="I should take my cat to the veterinarian.", country_hint="CA"),
            DetectLanguageInput(id="4", text="Este es un document escrito en Español.", country_hint="CA"),
            DetectLanguageInput(id="3", text="猫は幸せ"),
        ]

        response = await client.detect_language(docs, country_hint="US", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_country_hint_and_dict_per_item_hints(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 1
            country_str = "\"countryHint\": \"US\""
            country = resp.http_request.body.count(country_str)
            assert country == 2

        docs = [{"id": "1", "country_hint": "US", "text": "I will go to the park."},
                {"id": "2", "country_hint": "US", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs, country_hint="CA", raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"default_country_hint": "CA"})
    @recorded_by_proxy_async
    async def test_client_passed_default_country_hint(self, client):
        def callback(resp):
            country_str = "\"countryHint\": \"CA\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        def callback_2(resp):
            country_str = "\"countryHint\": \"DE\""
            country = resp.http_request.body.count(country_str)
            assert country == 3

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs, raw_response_hook=callback)
        response = await client.detect_language(docs, country_hint="DE", raw_response_hook=callback_2)
        response = await client.detect_language(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @recorded_by_proxy_async
    async def test_rotate_subscription_key(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        credential = AzureKeyCredential(textanalytics_test_api_key)
        client = TextAnalyticsClient(textanalytics_test_endpoint, credential)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs)
        assert response is not None

        credential.update("xxx")  # Make authentication fail
        with pytest.raises(ClientAuthenticationError):
            response = await client.detect_language(docs)

        credential.update(textanalytics_test_api_key)  # Authenticate successfully again
        response = await client.detect_language(docs)
        assert response is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_user_agent(self, client):
        def callback(resp):
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()) in resp.http_request.headers["User-Agent"]

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = await client.detect_language(docs, raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.detect_language(docs)

        # Attributes on DocumentError
        assert response[0].is_error
        assert response[0].id == "1"
        assert response[0].error is not None

        # Result attribute not on DocumentError, custom error message
        try:
            primary_language = response[0].primary_language
        except AttributeError as custom_error:
            assert custom_error.args[0] == \
                '\'DocumentError\' object has no attribute \'primary_language\'. ' \
                'The service was unable to process this document:\nDocument Id: 1\nError: ' \
                'InvalidDocument - Document text is empty.\n'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_attribute_error_nonexistent_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        response = await client.detect_language(docs)

        # Attribute not found on DocumentError or result obj, default behavior/message
        try:
            primary_language = response[0].attribute_not_on_result_or_error
        except AttributeError as default_behavior:
            assert default_behavior.args[0] == '\'DocumentError\' object has no attribute \'attribute_not_on_result_or_error\''

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = await client.detect_language(docs, model_version="bad")
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
                {"id": "2", "text": text}]

        doc_errors = await client.detect_language(docs)
        assert doc_errors[0].error.code == "InvalidDocument"
        assert doc_errors[0].error.message is not None
        assert doc_errors[1].error.code == "InvalidDocument"
        assert doc_errors[1].error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_warnings(self, client):
        # No warnings actually returned for detect_language. Will update when they add
        docs = [
            {"id": "1", "text": "This won't actually create a warning :'("},
        ]

        result = await client.detect_language(docs)
        for doc in result:
            doc_warnings = doc.warnings
            assert len(doc_warnings) == 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            await client.detect_language(docs)
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            await client.detect_language(docs)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            await client.detect_language(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = await client.detect_language(docs)
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
            response = await client.detect_language(docs)
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocumentBatch"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_country_hint_method(self, client):
        docs = [{"id": "1", "text": "hello world"}]

        response = await client.detect_language(docs, country_hint="United States")
        assert response[0].error.code == "InvalidCountryHint"
        assert response[0].error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_country_hint_docs(self, client):

        docs = [{"id": "1", "country_hint": "United States", "text": "hello world"}]

        response = await client.detect_language(docs)
        assert response[0].error.code == "InvalidCountryHint"
        assert response[0].error.message is not None

    @TextAnalyticsPreparer()
    @recorded_by_proxy_async
    async def test_country_hint_none(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        client = TextAnalyticsClient(textanalytics_test_endpoint, AzureKeyCredential(textanalytics_test_api_key))
        # service will eventually support this and we will not need to send "" for input == "none"
        documents = [{"id": "0", "country_hint": "none", "text": "This is written in English."}]
        documents2 = [DetectLanguageInput(id="1", country_hint="none", text="This is written in English.")]

        def callback(response):
            country_str = "\"countryHint\": \"\""
            country = response.http_request.body.count(country_str)
            assert country == 1

        # test dict
        result = await client.detect_language(documents, raw_response_hook=callback)
        # test DetectLanguageInput
        result2 = await client.detect_language(documents2, raw_response_hook=callback)
        # test per-operation
        result3 = await client.detect_language(documents=["this is written in english"], country_hint="none", raw_response_hook=callback)
        # test client default
        new_client = TextAnalyticsClient(textanalytics_test_endpoint, AzureKeyCredential(textanalytics_test_api_key), default_country_hint="none")
        result4 = await new_client.detect_language(documents=["this is written in english"], raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_country_hint_kwarg(self, client):
        def callback(response):
            country_str = "\"countryHint\": \"ES\""
            assert response.http_request.body.count(country_str) == 1
            assert response.model_version is not None
            assert response.statistics is not None

        res = await client.detect_language(
            documents=["this is written in english"],
            model_version="latest",
            show_stats=True,
            country_hint="ES",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @recorded_by_proxy_async
    async def test_pass_cls(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        text_analytics = TextAnalyticsClient(textanalytics_test_endpoint, AzureKeyCredential(textanalytics_test_api_key))
        res = await text_analytics.detect_language(
            documents=["Test passing cls to endpoint"],
            cls=callback
        )
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_0})
    @recorded_by_proxy_async
    async def test_string_index_type_not_fail_v3(self, client):
        # make sure that the addition of the string_index_type kwarg for v3.1-preview.1 doesn't
        # cause v3.0 calls to fail
        await client.detect_language(["please don't fail"])

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_disable_service_logs(self, client):
        def callback(resp):
            assert resp.http_request.query['loggingOptOut']
        await client.detect_language(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V2022_04_01_PREVIEW})
    @recorded_by_proxy_async
    async def test_disable_service_logs_body_param(self, client):
        def callback(resp):
            import json
            assert json.loads(resp.http_request.body)['parameters']['loggingOptOut']
        await client.detect_language(
            documents=["Test for logging disable"],
            disable_service_logs=True,
            raw_response_hook=callback,
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    async def test_language_multiapi_validate_args_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            res = await client.detect_language(["I'm tired"], disable_service_logs=True)
        assert str(e.value) == "'disable_service_logs' is only available for API version v3.1 and up.\n"
