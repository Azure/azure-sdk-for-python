# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_validation_info.py

DESCRIPTION:
    This sample demonstrates how to output the information that will help with manually
    validating your output from recognize custom forms.
USAGE:
    python sample_get_validation_info.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os


class GetValidationInfoSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

    def get_validation_info_from_recognize_custom_forms(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        with open("sample_forms/forms/Form_1.jpg", "rb") as f:
            poller = form_recognizer_client.begin_recognize_custom_forms(
                model_id=self.model_id, stream=f.read(), include_text_content=True
            )
        forms = poller.result()

        for idx, form in enumerate(forms):
            print("--------Recognizing Form #{}--------".format(idx))
            print("Form has type {}".format(form.form_type))
            for label, field in form.fields.items():
                # each field is of type FormField
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is not.
                print("Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                    label,
                    field.value,
                    field.value_data.text,
                    ", ".join(["[{}, {}]".format(p.x, p.y) for p in field.value_data.bounding_box]) if field.value_data.bounding_box else "N/A",
                    field.confidence
                ))
            for page in form.pages:
                print("Page {} has width '{}' and height '{}' measure with unit: {}, and has text angle '{}'".format(
                    page.page_number, page.width, page.height, page.unit, page.text_angle
                ))
                for table in page.tables:
                    for cell in table.cells:
                        print("Cell[{}][{}] has text '{}' with confidence {} based on the following words: ".format(
                            cell.row_index, cell.column_index, cell.text, cell.confidence
                        ))
                        # text_content only exists if you set include_text_content to True in your function call to recognize_custom_forms
                        # It is also a list of FormWords and FormLines, but in this example, we only deal with FormWords
                        for word in cell.text_content:
                            print("'{}' within bounding box '{}' with a confidence of {}".format(
                                word.text,
                                ", ".join(["[{}, {}]".format(p.x, p.y) for p in word.bounding_box]) if word.bounding_box else "N/A",
                                word.confidence
                            ))
            print("-----------------------------------")


if __name__ == '__main__':
    sample = GetValidationInfoSample()
    sample.get_validation_info_from_recognize_custom_forms()
