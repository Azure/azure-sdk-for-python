# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_automl_nlp.py
DESCRIPTION:
    These samples demonstrate how to use AutoML NLP functions
USAGE:
    python ml_samples_automl_nlp.py

"""

import os


class AutoMLNLPSamples(object):
    def automl_nlp_jobs():
        # [START automl.text_classification]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        test_classification_job = automl.text_classification(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="Sentiment",
            primary_metric="accuracy",
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.text_classification]

        # [START automl.text_classification_multilabel]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        text_classification_multilabel_job = automl.text_classification_multilabel(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="terms",
            primary_metric="accuracy",
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.text_classification_multilabel]

        # [START automl.text_ner]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        text_ner_job = automl.text_ner(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.text_ner]

        # [START automl.automl_nlp_job.text_classification_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        text_classification_job = automl.TextClassificationJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="terms",
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.automl_nlp_job.text_classification_job]

        # [START automl.text_classification_multilabel_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        text_classification_multilabel_job = automl.TextClassificationMultilabelJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="terms",
            primary_metric="accuracy",
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.text_classification_multilabel_job]

        # [START automl.text_ner_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        text_ner_job = automl.TextNerJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.text_ner_job]


if __name__ == "__main__":
    sample = AutoMLNLPSamples()
    sample.automl_nlp_jobs()
