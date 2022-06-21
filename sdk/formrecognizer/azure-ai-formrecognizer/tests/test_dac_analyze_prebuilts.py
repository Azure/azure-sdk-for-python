# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import json
import functools
from datetime import date, time
from devtools_testutils import recorded_by_proxy
from io import BytesIO
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.core.serialization import AzureJSONEncoder
from azure.ai.formrecognizer._generated.v2022_06_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult, FormContentType, AddressValue
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestDACAnalyzePrebuilts(FormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_business_card_multipage_pdf(self, client):
        with open(self.business_card_multipage_pdf, "rb") as fd:
            business_card = fd.read()

        poller = client.begin_analyze_document("prebuilt-businessCard", business_card)
        result = poller.result()
        assert len(result.documents) == 2
        business_card = result.documents[0]
        assert len(business_card.fields.get("ContactNames").value) == 1
        assert business_card.fields.get("ContactNames").value[0].value['FirstName'].value == 'JOHN'
        assert business_card.fields.get("ContactNames").value[0].value['LastName'].value == 'SINGER'

        assert len(business_card.fields.get("JobTitles").value) == 1
        assert business_card.fields.get("JobTitles").value[0].value == "Software Engineer"

        assert len(business_card.fields.get("Emails").value) == 1
        assert business_card.fields.get("Emails").value[0].value == "johnsinger@contoso.com"

        assert len(business_card.fields.get("Websites").value) == 1
        assert business_card.fields.get("Websites").value[0].value == "https://www.contoso.com"

        # FIXME: the service is not returning this currently
        # assert len(business_card.fields.get("OtherPhones").value) == 1
        # assert business_card.fields.get("OtherPhones").value[0].value == "+14257793479"

        business_card = result.documents[1]
        assert len(business_card.fields.get("ContactNames").value) == 1
        assert business_card.fields.get("ContactNames").value[0].value['FirstName'].value == 'Avery'
        assert business_card.fields.get("ContactNames").value[0].value['LastName'].value == 'Smith'

        assert len(business_card.fields.get("JobTitles").value) == 1
        assert business_card.fields.get("JobTitles").value[0].value == "Senior Researcher"

        assert len(business_card.fields.get("Departments").value) == 1
        assert business_card.fields.get("Departments").value[0].value == "Cloud & Al Department"

        assert len(business_card.fields.get("Emails").value) == 1
        assert business_card.fields.get("Emails").value[0].value == "avery.smith@contoso.com"

        assert len(business_card.fields.get("Websites").value) == 1
        assert business_card.fields.get("Websites").value[0].value == "https://www.contoso.com/"

        # The phone number values are not getting normalized to a phone number type. Just assert on text.
        assert len(business_card.fields.get("MobilePhones").value) == 1
        assert business_card.fields.get("MobilePhones").value[0].content == "+44 (0) 7911 123456"

        assert len(business_card.fields.get("WorkPhones").value) == 1
        assert business_card.fields.get("WorkPhones").value[0].content == "+44 (0) 20 9876 5432"

        assert len(business_card.fields.get("Faxes").value) == 1
        assert business_card.fields.get("Faxes").value[0].content == "+44 (0) 20 6789 2345"

        assert len(business_card.fields.get("Addresses").value) == 1
        assert business_card.fields.get("Addresses").value[0].value == "2 Kingdom Street\nPaddington, London, W2 6BD"

        assert len(business_card.fields.get("CompanyNames").value) == 1
        assert business_card.fields.get("CompanyNames").value[0].value == "Contoso"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_w2_png_value_address(self, client):
        with open(self.w2_png, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-tax.us.w2", document)

        result = poller.result()
        assert len(result.documents) == 1

        w2_document = result.documents[0]

        assert w2_document.doc_type == "tax.us.w2"
        assert w2_document.fields.get("TaxYear").value == "2018"
        # check value address correctly populated
        assert w2_document.fields.get("Employee").value.get("Address").value.house_number == "96541"
        assert w2_document.fields.get("Employee").value.get("Address").value.road == "molly hollow street"
        assert w2_document.fields.get("Employee").value.get("Address").value.postal_code == "98631-5293"
        assert w2_document.fields.get("Employee").value.get("Address").value.city == "kathrynmouth"
        assert w2_document.fields.get("Employee").value.get("Address").value.state == "ne"
        assert w2_document.fields.get("Employee").value.get("Address").value.street_address == "96541 molly hollow street"
        assert w2_document.fields.get("Employee").value.get("Address").value.country_region == None
        assert w2_document.fields.get("Employee").value.get("Address").value.po_box == None

        w2_dict = result.to_dict()
        json.dumps(w2_dict, cls=AzureJSONEncoder)
        result = AnalyzeResult.from_dict(w2_dict)

        assert w2_document.doc_type == "tax.us.w2"
        assert w2_document.fields.get("TaxYear").value == "2018"
        # check value address correctly populated
        assert w2_document.fields.get("Employee").value.get("Address").value.house_number == "96541"
        assert w2_document.fields.get("Employee").value.get("Address").value.road == "molly hollow street"
        assert w2_document.fields.get("Employee").value.get("Address").value.postal_code == "98631-5293"
        assert w2_document.fields.get("Employee").value.get("Address").value.city == "kathrynmouth"
        assert w2_document.fields.get("Employee").value.get("Address").value.state == "ne"
        assert w2_document.fields.get("Employee").value.get("Address").value.street_address == "96541 molly hollow street"
        assert w2_document.fields.get("Employee").value.get("Address").value.country_region == None
        assert w2_document.fields.get("Employee").value.get("Address").value.po_box == None

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_identity_document_jpg_passport(self, client):
        with open(self.identity_document_passport_jpg, "rb") as fd:
            id_document = fd.read()

        poller = client.begin_analyze_document("prebuilt-idDocument", id_document)

        result = poller.result()
        assert len(result.documents) == 1

        id_document = result.documents[0]

        passport = id_document.fields.get("MachineReadableZone").value
        assert passport["LastName"].value == "MARTIN"
        assert passport["FirstName"].value == "SARAH"
        assert passport["DocumentNumber"].value == "ZE000509"
        assert passport["DateOfBirth"].value == date(1985,1,1)
        assert passport["DateOfExpiration"].value == date(2023,1,14)
        assert passport["Sex"].value == "F"
        assert passport["CountryRegion"].value == "CAN"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_identity_document_jpg(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()

        poller = client.begin_analyze_document("prebuilt-idDocument", id_document)

        result = poller.result()
        assert len(result.documents) == 1
        id_document = result.documents[0]
        # check dict values
        assert id_document.fields.get("LastName").value == "TALBOT"
        assert id_document.fields.get("FirstName").value == "LIAM R."
        assert id_document.fields.get("DocumentNumber").value == "WDLABCD456DG"
        assert id_document.fields.get("DateOfBirth").value == date(1958,1,6)
        assert id_document.fields.get("DateOfExpiration").value == date(2020,8,12)
        assert id_document.fields.get("Sex").value == "M"
        assert id_document.fields.get("Address").value == "123 STREET ADDRESS\nYOUR CITY WA 99999-1234"
        assert id_document.fields.get("CountryRegion").value == "USA"
        assert id_document.fields.get("Region").value == "Washington"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_invoice_stream_transform_tiff(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_invoice = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.invoice_tiff, "rb") as fd:
            my_file = fd.read()

        poller = client.begin_analyze_document(
            model="prebuilt-invoice",
            document=my_file,
            cls=callback
        )

        result = poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_invoice_jpg(self, client, **kwargs):
        with open(self.invoice_jpg, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_analyze_document("prebuilt-invoice", invoice)

        result = poller.result()
        d = result.to_dict()
        json.dumps(d, cls=AzureJSONEncoder)
        result = AnalyzeResult.from_dict(d)
        assert len(result.documents) == 1
        invoice = result.documents[0]

        assert result.pages

        # check dict values
        assert invoice.fields.get("AmountDue").value.amount ==  610.0
        assert invoice.fields.get("AmountDue").value.symbol ==  "$"
        assert invoice.fields.get("BillingAddress").value, "123 Bill St, Redmond WA ==  98052"
        assert invoice.fields.get("BillingAddressRecipient").value ==  "Microsoft Finance"
        assert invoice.fields.get("CustomerAddress").value, "123 Other St, Redmond WA ==  98052"
        assert invoice.fields.get("CustomerAddressRecipient").value ==  "Microsoft Corp"
        assert invoice.fields.get("CustomerId").value ==  "CID-12345"
        assert invoice.fields.get("CustomerName").value ==  "MICROSOFT CORPORATION"
        assert invoice.fields.get("DueDate").value, date(2019, 12 ==  15)
        assert invoice.fields.get("InvoiceDate").value, date(2019, 11 ==  15)
        assert invoice.fields.get("InvoiceId").value ==  "INV-100"
        assert invoice.fields.get("InvoiceTotal").value.amount ==  110.0
        assert invoice.fields.get("PreviousUnpaidBalance").value.amount ==  500.0
        assert invoice.fields.get("PurchaseOrder").value ==  "PO-3333"
        assert invoice.fields.get("RemittanceAddress").value, "123 Remit St New York, NY ==  10001"
        assert invoice.fields.get("RemittanceAddressRecipient").value ==  "Contoso Billing"
        assert invoice.fields.get("ServiceAddress").value, "123 Service St, Redmond WA ==  98052"
        assert invoice.fields.get("ServiceAddressRecipient").value ==  "Microsoft Services"
        assert invoice.fields.get("ServiceEndDate").value, date(2019, 11 ==  14)
        assert invoice.fields.get("ServiceStartDate").value, date(2019, 10 ==  14)
        assert invoice.fields.get("ShippingAddress").value, "123 Ship St, Redmond WA ==  98052"
        assert invoice.fields.get("ShippingAddressRecipient").value ==  "Microsoft Delivery"
        assert invoice.fields.get("SubTotal").value.amount ==  100.0
        assert invoice.fields.get("SubTotal").value.symbol ==  "$"
        assert invoice.fields.get("TotalTax").value.amount ==  10.0
        assert invoice.fields.get("TotalTax").value.symbol ==  "$"
        assert invoice.fields.get("VendorName").value ==  "CONTOSO LTD."
        assert invoice.fields.get("VendorAddress").value, "123 456th St New York, NY ==  10001"
        assert invoice.fields.get("VendorAddressRecipient").value ==  "Contoso Headquarters"
        assert invoice.fields.get("Items").value[0].value["Amount"].value.amount ==  100.0
        assert invoice.fields.get("Items").value[0].value["Amount"].value.symbol ==  "$"
        assert invoice.fields.get("Items").value[0].value["Description"].value ==  "Consulting service"
        assert invoice.fields.get("Items").value[0].value["Quantity"].value ==  1.0
        assert invoice.fields.get("Items").value[0].value["UnitPrice"].value.amount ==  1.0
        assert invoice.fields.get("Items").value[0].value["UnitPrice"].value.symbol ==  None

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_fail_passing_content_type(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.receipt_png, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(TypeError):
            poller = client.begin_analyze_document(
                "prebuilt-receipt",
                my_file,
                content_type=FormContentType.IMAGE_PNG
            )

    @pytest.mark.skip("TODO check if the error type changed")
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_receipt_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        with open(self.receipt_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ServiceRequestError):
            client = DocumentAnalysisClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_analyze_document("prebuilt-receipt", my_file)

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            poller = client.begin_analyze_document("prebuilt-receipt", b"xx")

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with pytest.raises(HttpResponseError):
            poller = client.begin_analyze_document(
                "prebuilt-receipt",
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_damaged_file_passed_as_bytes_io(self, client):
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with pytest.raises(HttpResponseError):
            poller = client.begin_analyze_document(
                "prebuilt-receipt",
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_blank_page(self, client):

        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        poller = client.begin_analyze_document(
            "prebuilt-receipt",
            blank
        )
        result = poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_auto_detect_unsupported_stream_content(self, client):

        with open(self.unsupported_content_py, "rb") as fd:
            my_file = fd.read()

        with pytest.raises(HttpResponseError):
            poller = client.begin_analyze_document(
                "prebuilt-receipt",
                my_file
            )

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_stream_transform_png(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.receipt_png, "rb") as fd:
            my_file = fd.read()

        poller = client.begin_analyze_document(
            "prebuilt-receipt",
            document=my_file,
            cls=callback
        )

        result = poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_stream_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.receipt_jpg, "rb") as fd:
            my_file = fd.read()

        poller = client.begin_analyze_document(
            "prebuilt-receipt",
            document=my_file,
            cls=callback
        )

        result = poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_png(self, client):

        with open(self.receipt_png, "rb") as stream:
            poller = client.begin_analyze_document("prebuilt-receipt", stream)

        result = poller.result()
        assert len(result.documents) == 1
        receipt = result.documents[0]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("Subtotal").value ==  1098.99
        assert receipt.fields.get("TotalTax").value ==  104.4
        assert receipt.fields.get("Total").value ==  1203.39
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type ==  'receipt.retailMeal'

        assert len(result.pages) == 1

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_multipage(self, client):

        with open(self.multipage_receipt_pdf, "rb") as fd:
            receipt = fd.read()
        poller = client.begin_analyze_document("prebuilt-receipt", receipt)
        result = poller.result()

        d = result.to_dict()
        # this is simply checking that the dict is JSON serializable
        json.dumps(d, cls=AzureJSONEncoder)
        result = AnalyzeResult.from_dict(d)

        assert len(result.documents) == 2
        receipt = result.documents[0]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("MerchantPhoneNumber").value ==  '+19876543210'
        assert receipt.fields.get("Subtotal").value ==  11.7
        assert receipt.fields.get("TotalTax").value ==  1.17
        assert receipt.fields.get("Tip").value ==  1.63
        assert receipt.fields.get("Total").value ==  14.5
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type == "receipt.retailMeal"
        receipt = result.documents[1]
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("Subtotal").value ==  1098.99
        assert receipt.fields.get("TotalTax").value ==  104.4
        assert receipt.fields.get("Total").value ==  1203.39
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.doc_type == "receipt.retailMeal"

        assert len(result.pages) == 2

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_multipage_transform(self, client):

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.multipage_receipt_pdf, "rb") as fd:
            my_file = fd.read()

        poller = client.begin_analyze_document(
            "prebuilt-receipt",
            document=my_file,
            cls=callback
        )

        result = poller.result()
        raw_analyze_result = responses[0].analyze_result
        d = responses[1].to_dict()
        returned_model = AnalyzeResult.from_dict(d)

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_receipt_continuation_token(self, **kwargs):
        client = kwargs.pop("client")

        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()

        initial_poller = client.begin_analyze_document("prebuilt-receipt", receipt)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_analyze_document("prebuilt-receipt", None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_locale_specified(self, client):
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()
        poller = client.begin_analyze_document("prebuilt-receipt", receipt, locale="en-IN")
        assert 'en-IN' == poller._polling_method._initial_response.http_response.request.query['locale']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_receipt_locale_error(self, client):
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()
        with pytest.raises(HttpResponseError) as e:
            client.begin_analyze_document("prebuilt-receipt", receipt, locale="not a locale")
        assert "InvalidArgument" == e.value.error.code

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_pages_kwarg_specified(self, client):
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()

        poller = client.begin_analyze_document("prebuilt-receipt", receipt, pages="1")
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
