
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from azure.ai.formrecognizer import (
    FormRecognizerClient,
    FormTrainingClient,
    FormRecognizerApiVersion,
    AnalysisFeature,
    DocumentAnalysisApiVersion,
    DocumentAnalysisClient,
    DocumentModelAdministrationClient,
    ClassifierDocumentTypeDetails,
    BlobSource
)

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)
DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)
DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestMultiapi(FormRecognizerTest):

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_default_api_version_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer()
    def test_default_api_version_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_v2_0_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.0" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1})
    def test_v2_1_form_recognizer_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_1})
    def test_v2_1_form_training_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "v2.1" in client._client._client._base_url

    @FormRecognizerPreparer()
    def test_bad_api_version_form_recognizer_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormRecognizerClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_bad_api_version_form_training_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormTrainingClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_document_api_version_form_recognizer_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormRecognizerClient("url", "key", api_version="2023-07-31")
        assert "Unsupported API version '2023-07-31'. Please select from: {}\n" \
               "API version '2023-07-31' is " \
               "only available for DocumentAnalysisClient and DocumentModelAdministrationClient.".format(
            ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_document_api_version_form_training_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = FormTrainingClient("url", "key", api_version="2023-07-31")
        assert "Unsupported API version '2023-07-31'. Please select from: {}\nAPI version '2023-07-31' is " \
               "only available for DocumentAnalysisClient and DocumentModelAdministrationClient.".format(
            ", ".join(v.value for v in FormRecognizerApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_default_api_version_document_analysis_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "2023-07-31" == client._api_version

    @FormRecognizerPreparer()
    def test_bad_api_version_document_analysis_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentAnalysisClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_form_api_version_document_analysis_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version="2.1")
        assert "Unsupported API version '2.1'. Please select from: {}\nAPI version '2.1' is " \
               "only available for FormRecognizerClient and FormTrainingClient.".format(
            ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_default_api_version_document_model_admin_client(self, **kwargs):
        client = kwargs.pop("client")
        assert "2023-07-31" == client._api_version

    @FormRecognizerPreparer()
    def test_bad_api_version_document_model_admin_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version="9")
        assert "Unsupported API version '9'. Please select from: {}".format(
                ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @FormRecognizerPreparer()
    def test_form_api_version_document_model_admin_client(self):
        with pytest.raises(ValueError) as excinfo:
            client = DocumentModelAdministrationClient("url", "key", api_version="2.1")
        assert "Unsupported API version '2.1'. Please select from: {}\nAPI version '2.1' is " \
               "only available for FormRecognizerClient and FormTrainingClient.".format(
            ", ".join(v.value for v in DocumentAnalysisApiVersion)) == str(excinfo.value)

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    @recorded_by_proxy
    def test_v2_0_compatibility(self, client, formrecognizer_storage_container_sas_url_v2, **kwargs):
        # test that the addition of new attributes in v2.1 does not break v2.0

        label_poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=True)
        label_result = label_poller.result()

        unlabelled_poller = client.begin_training(formrecognizer_storage_container_sas_url_v2, use_training_labels=False)
        unlabelled_result = unlabelled_poller.result()

        assert label_result.properties is None
        assert label_result.model_name is None
        assert unlabelled_result.properties is None
        assert unlabelled_result.properties is None
        assert label_result.training_documents[0].model_id is None
        assert unlabelled_result.training_documents[0].model_id is None

        form_client = client.get_form_recognizer_client()
        label_poller = form_client.begin_recognize_custom_forms_from_url(label_result.model_id, self.form_url_jpg, include_field_elements=True)
        unlabelled_poller = form_client.begin_recognize_custom_forms_from_url(unlabelled_result.model_id, self.form_url_jpg, include_field_elements=True)


        label_form_result = label_poller.result()
        unlabelled_form_result = unlabelled_poller.result()

        assert unlabelled_form_result[0].form_type_confidence is None
        assert label_form_result[0].form_type_confidence is None
        assert unlabelled_form_result[0].pages[0].selection_marks is None
        assert label_form_result[0].pages[0].selection_marks is None
        assert unlabelled_form_result[0].pages[0].tables[0].bounding_box is None
        assert label_form_result[0].pages[0].tables[0].bounding_box is None
        assert unlabelled_form_result[0].pages[0].lines[0].appearance is None
        assert label_form_result[0].pages[0].lines[0].appearance is None

        models = client.list_custom_models()
        model = list(models)[0]

        assert model.model_name is None
        assert model.properties is None

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer(client_kwargs={"api_version": DocumentAnalysisApiVersion.V2022_08_31})
    @recorded_by_proxy
    def test_v2022_08_31_dac_compatibility(self, client, **kwargs):

        with open(self.multipage_table_pdf, "rb") as fd:
            my_file = fd.read()
        poller = client.begin_analyze_document("prebuilt-layout", my_file)
        layout = poller.result()
        assert len(layout.tables) == 3
        assert layout.tables[0].row_count == 30
        assert layout.tables[0].column_count == 5
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count == 5
        assert layout.tables[2].row_count == 24
        assert layout.tables[2].column_count == 5

        # test that the addition of new attributes in v2023-07-31 does not break v2022-08-31

        with pytest.raises(ValueError) as excinfo:
            client.begin_analyze_document("prebuilt-layout", my_file, features=[AnalysisFeature.STYLE_FONT])
        assert "Keyword argument 'features' is only available for API version V2023_07_31 and later." == str(excinfo.value)

        # test that the addition of new methods in v2023-07-31 does not break v2022-08-31
        with pytest.raises(ValueError) as excinfo:
            client.begin_classify_document("foo", my_file)
        assert (
                "Method 'begin_classify_document()' is only available for API version "
                "V2023_07_31 and later"
            ) == str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            client.begin_classify_document_from_url("foo", self.form_url_jpg)
            assert (
                "Method 'begin_classify_document_from_url()' is only available for API version "
                "V2023_07_31 and later"
            ) == str(excinfo.value)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer(client_kwargs={"api_version": DocumentAnalysisApiVersion.V2022_08_31})
    @recorded_by_proxy
    def test_v2022_08_31_dmac_compatibility(self, client, formrecognizer_storage_container_sas_url, formrecognizer_training_data_classifier, **kwargs):
        set_bodiless_matcher()
        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
        model = poller.result()

        assert model.model_id
        assert model.description is None
        assert model.created_on
        for name, doc_type in model.doc_types.items():
            assert name
            for key, field in doc_type.field_schema.items():
                assert key
                assert field["type"]
                assert doc_type.field_confidence[key] is not None

        # test that the addition of new attributes in v2023-07-31 does not break v2022-08-31

        with pytest.raises(ValueError) as excinfo:
            client.list_document_classifiers()
        assert (
            "Method 'list_document_classifiers()' is only available for API version "
            "V2023_07_31 and later") == str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            client.begin_build_document_classifier(
                        doc_types={
                            "IRS-1040-A": ClassifierDocumentTypeDetails(
                                source=BlobSource(
                                    container_url=formrecognizer_training_data_classifier,
                                    prefix="IRS-1040-A/train"
                                )
                            ),
                            "IRS-1040-B": ClassifierDocumentTypeDetails(
                                source=BlobSource(
                                    container_url=formrecognizer_training_data_classifier,
                                    prefix="IRS-1040-B/train"
                                )
                            ),
                            "IRS-1040-C": ClassifierDocumentTypeDetails(
                                source=BlobSource(
                                    container_url=formrecognizer_training_data_classifier,
                                    prefix="IRS-1040-C/train"
                                )
                            ),
                            "IRS-1040-D": ClassifierDocumentTypeDetails(
                                source=BlobSource(
                                    container_url=formrecognizer_training_data_classifier,
                                    prefix="IRS-1040-D/train"
                                )
                            ),
                            "IRS-1040-E": ClassifierDocumentTypeDetails(
                                source=BlobSource(
                                    container_url=formrecognizer_training_data_classifier,
                                    prefix="IRS-1040-E/train"
                                )
                            ),
                        },
                        description="IRS document classifier"
                    )
        assert (
            "Method 'begin_build_document_classifier()' is only available for API version "
            "V2023_07_31 and later") == str(excinfo.value)

        # test that the addition of new methods in v2023-07-31 does not break v2022-08-31
        with pytest.raises(ValueError) as excinfo:
            client.get_document_classifier("foo")
        assert (
                "Method 'get_document_classifier()' is only available for API version "
                "V2023_07_31 and later"
            ) == str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            client.delete_document_classifier("foo")
            assert (
                "Method 'delete_document_classifier()' is only available for API version "
                "V2023_07_31 and later"
            ) == str(excinfo.value)
