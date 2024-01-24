# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# --------------------------------------------------------

import logging
import os

import numpy as np
import pandas as pd
import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.ai.generative.evaluate import evaluate

logger = logging.getLogger(__name__)


@pytest.mark.e2etest
@pytest.mark.live_test_only
# @pytest.mark.usefixtures("recorded_test")
class TestEvaluate(AzureRecordedTestCase):

    def test_evaluate_built_in_metrics(self, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        test_data = [
            {"question": "How do you create a run?", "context": "AML API only",
             "answer": "To create a run using the Azure Machine Learning API, you first need to create an Experiment. Once you have an experiment, you can create a Run object that is associated with that experiment. Here is some Python code that demonstrates this process:\n\n```\nfrom azureml.core import Experiment, Run\nfrom azureml.core.workspace import Workspace\n\n# Define workspace and experiment\nws = Workspace.from_config()\nexp = Experiment(workspace=ws, name='my_experiment')\n\n# Create a new run\nrun = exp.start_logging()\n```\n\nIn this code, the `from_config()` method reads the configuration file that you created when you set up your Azure Machine Learning workspace. The `Experiment` constructor creates an Experiment object that is associated with your workspace, and the `start_logging()` method creates a new Run object that is associated with the Experiment. Now you can use the `run` object to log metrics, upload files, and track other information related to your machine learning experiment."},
            {"question": "How do you log a model?", "context": "Logging can be done using any OSS Sdk",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."},
        ]

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=test_data,
                task_type="qa",
                metrics_list=["gpt_groundedness"],
                model_config={
                    "api_version": "2023-07-01-preview",
                    "api_base": e2e_openai_api_base,
                    "api_type": "azure",
                    "api_key": e2e_openai_api_key,
                    "deployment_id": e2e_openai_completion_deployment_name,
                },
                data_mapping={
                    "questions": "question",
                    "contexts": "context",
                    "y_pred": "answer",
                    "y_test": "truth",
                },
                output_path=output_path
            )

            metrics_summary = result.metrics_summary
            tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

            assert "mean_gpt_groundedness" in metrics_summary.keys()
            assert metrics_summary.get("mean_gpt_groundedness") == np.nanmean(tabular_result["gpt_groundedness"])
