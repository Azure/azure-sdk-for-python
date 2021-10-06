# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiVersion, DocumentAnalysisClient
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)
FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestBusinessCardFromUrl(FormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_business_card_multipage_pdf(self, client):

        poller = client.begin_analyze_document_from_url("prebuilt-businessCard", self.business_card_multipage_url_pdf)
        result = poller.result()

        self.assertEqual(len(result.documents), 2)
        business_card = result.documents[0]
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'JOHN')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'SINGER')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Software Engineer")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "johnsinger@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com")

        self.assertEqual(len(business_card.fields.get("OtherPhones").value), 1)
        self.assertEqual(business_card.fields.get("OtherPhones").value[0].value, "+14257793479")

        business_card = result.documents[1]
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'Avery')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'Smith')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Senior Researcher")

        self.assertEqual(len(business_card.fields.get("Departments").value), 1)
        self.assertEqual(business_card.fields.get("Departments").value[0].value, "Cloud & Al Department")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "avery.smith@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com/")

        # The phone number values are not getting normalized to a phone number type. Just assert on text.
        self.assertEqual(len(business_card.fields.get("MobilePhones").value), 1)
        self.assertEqual(business_card.fields.get("MobilePhones").value[0].content, "+44 (0) 7911 123456")

        self.assertEqual(len(business_card.fields.get("WorkPhones").value), 1)
        self.assertEqual(business_card.fields.get("WorkPhones").value[0].content, "+44 (0) 20 9876 5432")

        self.assertEqual(len(business_card.fields.get("Faxes").value), 1)
        self.assertEqual(business_card.fields.get("Faxes").value[0].content, "+44 (0) 20 6789 2345")

        self.assertEqual(len(business_card.fields.get("Addresses").value), 1)
        self.assertEqual(business_card.fields.get("Addresses").value[0].value, "2 Kingdom Street Paddington, London, W2 6BD")

        self.assertEqual(len(business_card.fields.get("CompanyNames").value), 1)
        self.assertEqual(business_card.fields.get("CompanyNames").value[0].value, "Contoso")

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_business_card_jpg_include_field_elements(self, client):
        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, include_field_elements=True)

        result = poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]

        self.assertFormPagesHasValues(business_card.pages)

        for name, field in business_card.fields.items():
            for f in field.value:
                self.assertFieldElementsHasValues(f.value_data.field_elements, business_card.page_range.first_page_number)
        
        # check dict values
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value_data.page_number, 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'Avery')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'Smith')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Senior Researcher")

        self.assertEqual(len(business_card.fields.get("Departments").value), 1)
        self.assertEqual(business_card.fields.get("Departments").value[0].value, "Cloud & Al Department")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "avery.smith@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com/")

        # The phone number values are not getting normalized to a phone number type. Just assert on text.
        self.assertEqual(len(business_card.fields.get("MobilePhones").value), 1)
        self.assertEqual(business_card.fields.get("MobilePhones").value[0].value_data.text, "+44 (0) 7911 123456")

        self.assertEqual(len(business_card.fields.get("WorkPhones").value), 1)
        self.assertEqual(business_card.fields.get("WorkPhones").value[0].value_data.text, "+44 (0) 20 9876 5432")

        self.assertEqual(len(business_card.fields.get("Faxes").value), 1)
        self.assertEqual(business_card.fields.get("Faxes").value[0].value_data.text, "+44 (0) 20 6789 2345")

        self.assertEqual(len(business_card.fields.get("Addresses").value), 1)
        self.assertEqual(business_card.fields.get("Addresses").value[0].value, "2 Kingdom Street Paddington, London, W2 6BD")

        self.assertEqual(len(business_card.fields.get("CompanyNames").value), 1)
        self.assertEqual(business_card.fields.get("CompanyNames").value[0].value, "Contoso")

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_business_card_v2(self, client):
        with pytest.raises(ValueError) as e:
            client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
        assert "Method 'begin_recognize_business_cards_from_url' is only available for API version V2_1 and up" in str(e.value)
