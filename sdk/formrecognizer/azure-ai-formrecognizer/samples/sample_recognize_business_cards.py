# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_business_cards.py

DESCRIPTION:
    This sample demonstrates how to recognize fields on business cards.

    See fields found on a business card here:
    https://aka.ms/formrecognizer/businesscardfields

USAGE:
    python sample_recognize_business_cards.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


class RecognizeBusinessCardSample(object):

    def recognize_business_card(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./sample_forms/business_cards/business-card-english.jpg"))
        # [START recognize_business_cards]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_business_cards(business_card=f, locale="en-US")
        business_cards = poller.result()

        for idx, business_card in enumerate(business_cards):
            print("--------Recognizing business card #{}--------".format(idx+1))
            contact_names = business_card.fields.get("ContactNames")
            if contact_names:
                for contact_name in contact_names.value:
                    print("Contact First Name: {} has confidence: {}".format(
                        contact_name.value["FirstName"].value, contact_name.value["FirstName"].confidence
                    ))
                    print("Contact Last Name: {} has confidence: {}".format(
                        contact_name.value["LastName"].value, contact_name.value["LastName"].confidence
                    ))
            company_names = business_card.fields.get("CompanyNames")
            if company_names:
                for company_name in company_names.value:
                    print("Company Name: {} has confidence: {}".format(company_name.value, company_name.confidence))
            departments = business_card.fields.get("Departments")
            if departments:
                for department in departments.value:
                    print("Department: {} has confidence: {}".format(department.value, department.confidence))
            job_titles = business_card.fields.get("JobTitles")
            if job_titles:
                for job_title in job_titles.value:
                    print("Job Title: {} has confidence: {}".format(job_title.value, job_title.confidence))
            emails = business_card.fields.get("Emails")
            if emails:
                for email in emails.value:
                    print("Email: {} has confidence: {}".format(email.value, email.confidence))
            websites = business_card.fields.get("Websites")
            if websites:
                for website in websites.value:
                    print("Website: {} has confidence: {}".format(website.value, website.confidence))
            addresses = business_card.fields.get("Addresses")
            if addresses:
                for address in addresses.value:
                    print("Address: {} has confidence: {}".format(address.value, address.confidence))
            mobile_phones = business_card.fields.get("MobilePhones")
            if mobile_phones:
                for phone in mobile_phones.value:
                    print("Mobile phone number: {} has confidence: {}".format(phone.value, phone.confidence))
            faxes = business_card.fields.get("Faxes")
            if faxes:
                for fax in faxes.value:
                    print("Fax number: {} has confidence: {}".format(fax.value, fax.confidence))
            work_phones = business_card.fields.get("WorkPhones")
            if work_phones:
                for work_phone in work_phones.value:
                    print("Work phone number: {} has confidence: {}".format(work_phone.value, work_phone.confidence))
            other_phones = business_card.fields.get("OtherPhones")
            if other_phones:
                for other_phone in other_phones.value:
                    print("Other phone number: {} has confidence: {}".format(other_phone.value, other_phone.confidence))
        # [END recognize_business_cards]

    def recognize_business_card_by_attribute(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./sample_forms/business_cards/business-card-english.jpg"))

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_business_cards(business_card=f, locale="en-US")
        business_cards = poller.result()

        for idx, business_card in enumerate(business_cards):
            print("--------Recognizing business card #{}--------".format(idx+1))
            for contact_name in business_card.fields.contact_names.value:
                print("Contact First Name: {} has confidence: {}".format(
                    contact_name.first_name.value, contact_name.first_name.confidence
                ))
                print("Contact Last Name: {} has confidence: {}".format(
                    contact_name.last_name.value, contact_name.last_name.confidence
                ))
            for dept in business_card.fields.departments.value:
                print("Departments: {} has confidence {}".format(dept.value, dept.confidence))
            for company_name in business_card.fields.company_names.value:
                print("CompanyNames: {} has confidence {}".format(company_name.value, company_name.confidence))
            for job_title in business_card.fields.job_titles.value:
                print("JobTitles: {} has confidence {}".format(job_title.value, job_title.confidence))
            for email in business_card.fields.emails.value:
                print("Emails: {} has confidence {}".format(email.value, email.confidence))
            for website in business_card.fields.websites.value:
                print("Websites: {} has confidence {}".format(website.value, website.confidence))
            for address in business_card.fields.addresses.value:
                print("Addresses: {} has confidence {}".format(address.value, address.confidence))
            for phone in business_card.fields.mobile_phones.value:
                print("MobilePhones: {} has confidence {}".format(phone.value, phone.confidence))
            for fax in business_card.fields.faxes.value:
                print("Faxes: {} has confidence {}".format(fax.value, fax.confidence))
            for phone in business_card.fields.work_phones.value:
                print("WorkPhones: {} has confidence {}".format(phone.value, phone.confidence))
            for phone in business_card.fields.other_phones.value:
                print("OtherPhones: {} has confidence {}".format(phone.value, phone.confidence))


if __name__ == '__main__':
    sample = RecognizeBusinessCardSample()
    sample.recognize_business_card()
    sample.recognize_business_card_by_attribute()
