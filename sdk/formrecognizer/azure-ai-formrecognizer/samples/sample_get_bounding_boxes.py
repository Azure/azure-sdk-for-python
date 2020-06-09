# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_bounding_boxes.py

DESCRIPTION:
    This sample demonstrates how to get detailed information to visualize the outlines of
    form content and fields, which can be used for manual validation and drawing UI as part of an application.
USAGE:
    python sample_get_bounding_boxes.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class GetBoundingBoxesSample(object):

    def get_bounding_boxes(self):
        from azure.ai.formrecognizer import FormWord, FormLine
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        # Make sure your form's type is included in the list of form types the custom model can recognize
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_custom_forms(
                model_id=model_id, form=f, include_text_content=True
            )
        forms = poller.result()

        for idx, form in enumerate(forms):
            print("--------RECOGNIZING FORM #{}--------".format(idx))
            print("Form has type {}".format(form.form_type))
            for name, field in form.fields.items():
                # each field is of type FormField
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is not.
                print("...Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                    name,
                    field.value,
                    field.value_data.text,
                    format_bounding_box(field.value_data.bounding_box),
                    field.confidence
                ))
            for page in form.pages:
                print("-------Recognizing Page #{} of Form #{}-------".format(page.page_number, idx))
                print("Has width '{}' and height '{}' measure with unit: {}, and has text angle '{}'".format(
                    page.width, page.height, page.unit, page.text_angle
                ))
                for table in page.tables:
                    for cell in table.cells:
                        print("...Cell[{}][{}] has text '{}' with confidence {} based on the following words: ".format(
                            cell.row_index, cell.column_index, cell.text, cell.confidence
                        ))
                        # text_content is only populated if you set include_text_content to True in your function call to recognize_custom_forms
                        # It is a heterogeneous list of FormWord and FormLine.
                        for content in cell.text_content:
                            if isinstance(content, FormWord):
                                print("......Word '{}' within bounding box '{}' has a confidence of {}".format(
                                    content.text,
                                    format_bounding_box(content.bounding_box),
                                    content.confidence
                                ))
                            elif isinstance(content, FormLine):
                                print("......Line '{}' within bounding box '{}' has the following words: ".format(
                                    content.text,
                                    format_bounding_box(content.bounding_box)
                                ))
                                for word in content.words:
                                    print(".........Word '{}' within bounding box '{}' has a confidence of {}".format(
                                        word.text,
                                        format_bounding_box(word.bounding_box),
                                        word.confidence
                                    ))

                print("---------------------------------------------------")
            print("-----------------------------------")


if __name__ == '__main__':
    sample = GetBoundingBoxesSample()
    sample.get_bounding_boxes()
