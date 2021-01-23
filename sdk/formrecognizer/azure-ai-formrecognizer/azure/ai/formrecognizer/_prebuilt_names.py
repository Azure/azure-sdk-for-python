# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

SCHEMA = {
    "BusinessCard": {
        "ContactNames": {
            "FirstName": "string",
            "LastName": "string",
        },
        "CompanyNames": "list",
        "Departments": "list",
        "JobTitles": "list",
        "Emails": "list",
        "Websites": "list",
        "Addresses": "list",
        "MobilePhones": "list",
        "Faxes": "list",
        "WorkPhones": "list",
        "OtherPhones": "list"
    },
    "Receipt": {
        "ReceiptType": "string",
        "MerchantName": "string",
        "MerchantPhoneNumber": "phoneNumber",
        "MerchantAddress": "string",
        "TransactionDate": "date",
        "TransactionTime": "time",
        "Total": "float",
        "Subtotal": "float",
        "Tax": "float",
        "Tip": "float",
        "Items": {
            "Name": "string",
            "Quantity": "float",
            "Price": "float",
            "TotalPrice": "float",
        }
    },
    "Invoice": {
        "CustomerName": "string",
        "CustomerId": "string",
        "PurchaseOrder": "string",
        "InvoiceId": "string",
        "InvoiceDate": "date",
        "DueDate": "date",
        "VendorName": "string",
        "VendorAddress": "string",
        "VendorAddressRecipient": "string",
        "CustomerAddress": "string",
        "CustomerAddressRecipient": "string",
        "BillingAddress": "string",
        "BillingAddressRecipient": "string",
        "ShippingAddress": "string",
        "ShippingAddressRecipient": "string",
        "SubTotal": "float",
        "TotalTax": "float",
        "InvoiceTotal": "float",
        "PreviousUnpaidBalance": "float",
        "AmountDue": "float",
        "ServiceStartDate": "date",
        "ServiceEndDate": "date",
        "ServiceAddress": "string",
        "ServiceAddressRecipient": "string",
        "RemittanceAddress": "string",
        "RemittanceAddressRecipient": "string",
    }
}
