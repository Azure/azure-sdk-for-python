# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_business_cards.py

DESCRIPTION:
    This sample demonstrates how to analyze business cards.

    See fields found on a business card here:
    https://aka.ms/azsdk/formrecognizer/businesscardfieldschema

USAGE:
    python sample_analyze_business_cards.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


def analyze_business_card():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./sample_forms/business_cards/business-card-english.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-businessCard", document=f, locale="en-US"
        )
    business_cards = poller.result()

    for idx, business_card in enumerate(business_cards.documents):
        print(f"--------Analyzing business card #{idx + 1}--------")
        contact_names = business_card.fields.get("ContactNames")
        if contact_names:
            for contact_name in contact_names.value:
                print(
                    f"Contact First Name: {contact_name.value['FirstName'].value} "
                    f"has confidence: {contact_name.value['FirstName'].confidence}"
                )
                print(
                    f"Contact Last Name: {contact_name.value['LastName'].value} has"
                    f" confidence: {contact_name.value['LastName'].confidence}"
                )
        company_names = business_card.fields.get("CompanyNames")
        if company_names:
            for company_name in company_names.value:
                print(
                    f"Company Name: {company_name.value} has confidence: {company_name.confidence}"
                )
        departments = business_card.fields.get("Departments")
        if departments:
            for department in departments.value:
                print(
                    f"Department: {department.value} has confidence: {department.confidence}"
                )
        job_titles = business_card.fields.get("JobTitles")
        if job_titles:
            for job_title in job_titles.value:
                print(
                    f"Job Title: {job_title.value} has confidence: {job_title.confidence}"
                )
        emails = business_card.fields.get("Emails")
        if emails:
            for email in emails.value:
                print(f"Email: {email.value} has confidence: {email.confidence}")
        websites = business_card.fields.get("Websites")
        if websites:
            for website in websites.value:
                print(f"Website: {website.value} has confidence: {website.confidence}")
        addresses = business_card.fields.get("Addresses")
        if addresses:
            for address in addresses.value:
                print(f"Address: {address.value} has confidence: {address.confidence}")
        mobile_phones = business_card.fields.get("MobilePhones")
        if mobile_phones:
            for phone in mobile_phones.value:
                print(
                    f"Mobile phone number: {phone.content} has confidence: {phone.confidence}"
                )
        faxes = business_card.fields.get("Faxes")
        if faxes:
            for fax in faxes.value:
                print(f"Fax number: {fax.content} has confidence: {fax.confidence}")
        work_phones = business_card.fields.get("WorkPhones")
        if work_phones:
            for work_phone in work_phones.value:
                print(
                    f"Work phone number: {work_phone.content} has confidence: {work_phone.confidence}"
                )
        other_phones = business_card.fields.get("OtherPhones")
        if other_phones:
            for other_phone in other_phones.value:
                print(
                    f"Other phone number: {other_phone.value} has confidence: {other_phone.confidence}"
                )


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        analyze_business_card()
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
