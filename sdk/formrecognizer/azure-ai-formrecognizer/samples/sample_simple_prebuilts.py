# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os


class SimplePrebuilt(object):

    def simple_receipts(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        poller = form_recognizer_client.begin_recognize_receipts_from_url(receipt_url=url)
        receipts = poller.result()

        for receipt in receipts:
            print("Receipt Type: {} has confidence: {}".format(receipt.ReceiptType.value, receipt.ReceiptType.confidence))
            print("Merchant Name: {} has confidence: {}".format(receipt.MerchantName.value, receipt.MerchantName.confidence))
            print("Transaction Date: {} has confidence: {}".format(receipt.TransactionDate.value, receipt.TransactionDate.confidence))
            print("Receipt items:")
            for item in receipt.Items.value:
                print("...Item Name: {} has confidence: {}".format(item.Name.value, item.Name.confidence))
                print("...Item Quantity: {} has confidence: {}".format(item.Quantity.value, item.Quantity.confidence))
                print("...Individual Item Price: {} has confidence: {}".format(item.Price.value, item.Price.confidence))
                print("...Total Item Price: {} has confidence: {}".format(item.TotalPrice.value, item.TotalPrice.confidence))
            print("Subtotal: {} has confidence: {}".format(receipt.Subtotal.value, receipt.Subtotal.confidence))
            print("Tax: {} has confidence: {}".format(receipt.Tax.value, receipt.Tax.confidence))
            print("Tip: {} has confidence: {}".format(receipt.Tip.value, receipt.Tip.confidence))
            print("Total: {} has confidence: {}".format(receipt.Total.value, receipt.Total.confidence))

    def simple_business_cards(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./sample_forms/business_cards/business-card-english.jpg"))
        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_business_cards(business_card=f, locale="en-US")

        business_cards = poller.result()

        for business_card in business_cards:
            print("Contact Names:")
            for contact_name in business_card.ContactNames.value:
                print("...FirstName: {} has confidence {}".format(contact_name.FirstName.value, contact_name.FirstName.confidence))
                print("...LastName: {} has confidence {}".format(contact_name.LastName.value, contact_name.LastName.confidence))
            for dept in business_card.Departments.value:
                print("Departments: {} has confidence {}".format(dept.value, dept.confidence))
            for company_name in business_card.CompanyNames.value:
                print("CompanyNames: {} has confidence {}".format(company_name.value, company_name.confidence))
            for job_title in business_card.JobTitles.value:
                print("JobTitles: {} has confidence {}".format(job_title.value, job_title.confidence))
            for email in business_card.Emails.value:
                print("Emails: {} has confidence {}".format(email.value, email.confidence))
            for website in business_card.Websites.value:
                print("Websites: {} has confidence {}".format(website.value, website.confidence))
            for address in business_card.Addresses.value:
                print("Addresses: {} has confidence {}".format(address.value, address.confidence))
            for phone in business_card.MobilePhones.value:
                print("MobilePhones: {} has confidence {}".format(phone.value, phone.confidence))
            for phone in business_card.WorkPhones.value:
                print("WorkPhones: {} has confidence {}".format(phone.value, phone.confidence))
            for phone in business_card.OtherPhones.value:
                print("OtherPhones: {} has confidence {}".format(phone.value, phone.confidence))

    def simple_invoices(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        poller = form_recognizer_client.begin_recognize_invoices_from_url("https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/media/sample-invoice.jpg")
        invoices = poller.result()

        for invoice in invoices:
            print("CustomerName: {} has confidence {}".format(invoice.CustomerName.value, invoice.CustomerName.confidence))
            print("CustomerId: {} has confidence {}".format(invoice.CustomerId.value, invoice.CustomerId.confidence))
            print("PurchaseOrder: {} has confidence {}".format(invoice.PurchaseOrder.value, invoice.PurchaseOrder.confidence))
            print("InvoiceId: {} has confidence {}".format(invoice.InvoiceId.value, invoice.InvoiceId.confidence))
            print("InvoiceDate: {} has confidence {}".format(invoice.InvoiceDate.value, invoice.InvoiceDate.confidence))
            print("DueDate: {} has confidence {}".format(invoice.DueDate.value, invoice.DueDate.confidence))
            print("VendorName: {} has confidence {}".format(invoice.VendorName.value, invoice.VendorName.confidence))
            print("VendorAddress: {} has confidence {}".format(invoice.VendorAddress.value, invoice.VendorAddress.confidence))
            print("VendorAddressRecipient: {} has confidence {}".format(invoice.VendorAddressRecipient.value, invoice.VendorAddressRecipient.confidence))
            print("CustomerAddress: {} has confidence {}".format(invoice.CustomerAddress.value, invoice.CustomerAddress.confidence))
            print("CustomerAddressRecipient: {} has confidence {}".format(invoice.CustomerAddressRecipient.value, invoice.CustomerAddressRecipient.confidence))
            print("BillingAddress: {} has confidence {}".format(invoice.BillingAddress.value, invoice.BillingAddress.confidence))
            print("BillingAddressRecipient: {} has confidence {}".format(invoice.BillingAddressRecipient.value, invoice.BillingAddressRecipient.confidence))
            print("ShippingAddress: {} has confidence {}".format(invoice.ShippingAddress.value, invoice.ShippingAddress.confidence))
            print("ShippingAddressRecipient: {} has confidence {}".format(invoice.ShippingAddressRecipient.value, invoice.ShippingAddressRecipient.confidence))
            print("SubTotal: {} has confidence {}".format(invoice.SubTotal.value, invoice.SubTotal.confidence))
            print("TotalTax: {} has confidence {}".format(invoice.TotalTax.value, invoice.TotalTax.confidence))
            print("InvoiceTotal: {} has confidence {}".format(invoice.InvoiceTotal.value, invoice.InvoiceTotal.confidence))
            print("PreviousUnpaidBalance: {} has confidence {}".format(invoice.PreviousUnpaidBalance.value, invoice.PreviousUnpaidBalance.confidence))
            print("AmountDue: {} has confidence {}".format(invoice.AmountDue.value, invoice.AmountDue.confidence))
            print("ServiceStartDate: {} has confidence {}".format(invoice.ServiceStartDate.value, invoice.ServiceStartDate.confidence))
            print("ServiceEndDate: {} has confidence {}".format(invoice.ServiceEndDate.value, invoice.ServiceEndDate.confidence))
            print("ServiceAddress: {} has confidence {}".format(invoice.ServiceAddress.value, invoice.ServiceAddress.confidence))
            print("ServiceAddressRecipient: {} has confidence {}".format(invoice.ServiceAddressRecipient.value, invoice.ServiceAddressRecipient.confidence))
            print("RemittanceAddress: {} has confidence {}".format(invoice.RemittanceAddress.value, invoice.RemittanceAddress.confidence))
            print("RemittanceAddressRecipient: {} has confidence {}".format(invoice.RemittanceAddressRecipient.value, invoice.RemittanceAddressRecipient.confidence))


if __name__ == '__main__':
    sample = SimplePrebuilt()
    sample.simple_receipts()
    sample.simple_business_cards()
    sample.simple_invoices()
