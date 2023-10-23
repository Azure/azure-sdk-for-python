# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.metrics import constants

TYPE_TO_KWARGS_MAPPING = {
    constants.QUESTION_ANSWERING: ["questions", "contexts", "y_pred", "y_test"]
}
