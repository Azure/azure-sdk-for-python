# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_composed_model_async.py

DESCRIPTION:
    Model compose allows multiple models to be composed and called with a single model ID.
    This is useful when you have trained different models and want to aggregate a group of
    them into a single model that you (or a user) could use to recognize a form. When doing
    so, you can let the service decide which model more accurately represents the form to
    recognize, instead of manually trying each trained model against the form and selecting
    the most accurate one.

    In our case, we will be writing an application that collects the expenses a company is making.
    There are 4 main areas where we get purchase orders from (office supplies, office equipment,
    furniture, and cleaning supplies). Because each area has its own form with its own structure,
    we need to train a model per form. Note that you can substitute your own models or container
    SAS URLs for this sample.

USAGE:
    python sample_create_composed_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) PURCHASE_ORDER_OFFICE_SUPPLIES_SAS_URL_V2 - a container SAS URL to your Azure Storage blob container.
    4) PURCHASE_ORDER_OFFICE_EQUIPMENT_SAS_URL_V2 - a container SAS URL to your Azure Storage blob container.
    5) PURCHASE_ORDER_OFFICE_FURNITURE_SAS_URL_V2 - a container SAS URL to your Azure Storage blob container.
    6) PURCHASE_ORDER_OFFICE_CLEANING_SUPPLIES_SAS_URL_V2 - a container SAS URL to your Azure Storage blob container.
"""

import os
import asyncio


class ComposedModelSampleAsync(object):

    async def create_composed_model_async(self):
        # [START begin_create_composed_model_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        po_supplies = os.environ['PURCHASE_ORDER_OFFICE_SUPPLIES_SAS_URL_V2']
        po_equipment = os.environ['PURCHASE_ORDER_OFFICE_EQUIPMENT_SAS_URL_V2']
        po_furniture = os.environ['PURCHASE_ORDER_OFFICE_FURNITURE_SAS_URL_V2']
        po_cleaning_supplies = os.environ['PURCHASE_ORDER_OFFICE_CLEANING_SUPPLIES_SAS_URL_V2']

        form_training_client = FormTrainingClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        async with form_training_client:
            supplies_poller = await form_training_client.begin_training(
                po_supplies, use_training_labels=True, model_name="Purchase order - Office supplies"
            )
            equipment_poller = await form_training_client.begin_training(
                po_equipment, use_training_labels=True, model_name="Purchase order - Office Equipment"
            )
            furniture_poller = await form_training_client.begin_training(
                po_furniture, use_training_labels=True, model_name="Purchase order - Furniture"
            )
            cleaning_supplies_poller = await form_training_client.begin_training(
                po_cleaning_supplies, use_training_labels=True, model_name="Purchase order - Cleaning Supplies"
            )
            supplies_model = await supplies_poller.result()
            equipment_model = await equipment_poller.result()
            furniture_model = await furniture_poller.result()
            cleaning_supplies_model = await cleaning_supplies_poller.result()

            models_trained_with_labels = [
                supplies_model.model_id,
                equipment_model.model_id,
                furniture_model.model_id,
                cleaning_supplies_model.model_id
            ]

            poller = await form_training_client.begin_create_composed_model(
                models_trained_with_labels, model_name="Office Supplies Composed Model"
            )
            model = await poller.result()

        print("Office Supplies Composed Model Info:")
        print("Model ID: {}".format(model.model_id))
        print("Model name: {}".format(model.model_name))
        print("Is this a composed model?: {}".format(model.properties.is_composed_model))
        print("Status: {}".format(model.status))
        print("Composed model creation started on: {}".format(model.training_started_on))
        print("Creation completed on: {}".format(model.training_completed_on))

        # [END begin_create_composed_model_async]

        print("Recognized fields:")
        for submodel in model.submodels:
            print("The submodel has model ID: {}".format(submodel.model_id))
            print("...The submodel with form type {} has an average accuracy '{}'".format(
                submodel.form_type, submodel.accuracy
            ))
            for name, field in submodel.fields.items():
                print("...The model found the field '{}' with an accuracy of {}".format(
                    name, field.accuracy
                ))

        # Training result information
        for doc in model.training_documents:
            print("Document was used to train model with ID: {}".format(doc.model_id))
            print("Document name: {}".format(doc.name))
            print("Document status: {}".format(doc.status))
            print("Document page count: {}".format(doc.page_count))
            print("Document errors: {}".format(doc.errors))


async def main():
    sample = ComposedModelSampleAsync()
    await sample.create_composed_model_async()


if __name__ == '__main__':
    asyncio.run(main())
