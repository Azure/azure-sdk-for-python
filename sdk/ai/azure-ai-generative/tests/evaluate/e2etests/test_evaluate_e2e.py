# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# --------------------------------------------------------

import logging
import os
import pathlib

import numpy as np
import pandas as pd
import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.ai.generative.evaluate import evaluate
from azure.ai.resources.entities import AzureOpenAIModelConfiguration

logger = logging.getLogger(__name__)


@pytest.mark.e2etest
@pytest.mark.live_test_only
@pytest.mark.usefixtures("recorded_test")
class TestEvaluate(AzureRecordedTestCase):

    def test_evaluate_built_in_metrics(self, ai_client, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        test_data = [
            {"context": "Some are reported as not having been wanted at all.",
             "question": "are all reported as being wanted?",
             "answer": "All are reported as being completely and fully wanted."
            },
            {"question": "How do you log a model?",
             "context": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`.",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."
            },
        ]

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"
            tracking_uri = ai_client.tracking_uri

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=test_data,
                task_type="qa",
                metrics_list=["gpt_groundedness", "gpt_relevance"],
                model_config={
                    "api_version": "2023-07-01-preview",
                    "api_base": e2e_openai_api_base,
                    "api_type": "azure",
                    "api_key": e2e_openai_api_key,
                    "deployment_id": e2e_openai_completion_deployment_name,
                },
                data_mapping={
                    "question": "question",
                    "context": "context",
                    "y_pred": "answer",
                    "y_test": "truth",
                },
                tracking_uri=tracking_uri,
                output_path=output_path
            )

            metrics_summary = result.metrics_summary
            tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

            assert "gpt_groundedness" in metrics_summary.keys()
            assert "gpt_relevance" in metrics_summary.keys()
            assert metrics_summary.get("gpt_relevance") == np.nanmean(tabular_result["gpt_relevance"])
            assert tabular_result["gpt_groundedness"][0] in [1, 2]
            assert tabular_result["gpt_groundedness"][1] in ["n/a"]
            assert tabular_result["gpt_relevance"][0] in [1, 2]
            assert tabular_result["gpt_relevance"][1] in [4, 5]

    def test_evaluate_built_in_qa_fallback_groundedness(self, e2e_openai_api_base, e2e_openai_api_key,
                                                        e2e_openai_completion_deployment_name, tmpdir):
        test_data = [
            {"context": "Some are reported as not having been wanted at all.",
             "question": "",
             "answer": "All are reported as being completely and fully wanted."
            },
            {"question": "How do you log a model?",
             "context": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`.",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."
            },
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
                    "question": "question",
                    "context": "context",
                    "y_pred": "answer",
                    "y_test": "truth",
                },
                output_path=output_path
            )

            metrics_summary = result.metrics_summary
            tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

            assert "gpt_groundedness" in metrics_summary.keys()
            assert metrics_summary.get("gpt_groundedness") == np.nanmean(tabular_result["gpt_groundedness"])
            assert tabular_result["gpt_groundedness"][0] in [1, 2]
            assert tabular_result["gpt_groundedness"][1] in [4, 5]

    def test_evaluate_built_in_metrics_missing_model_config(self, tmpdir):
        test_data = [
            {"context": "Some are reported as not having been wanted at all.",
             "question": "",
             "answer": "All are reported as being completely and fully wanted."
            },
            {"question": "How do you log a model?",
             "context": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`.",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."
            },
        ]

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"

            with pytest.raises(Exception) as ex:
                result = evaluate(  # This will log metric/artifacts using mlflow
                    evaluation_name="rag-chat-1",
                    data=test_data,
                    task_type="qa",
                    metrics_list=["gpt_relevance"],
                    data_mapping={
                        "question": "question",
                        "context": "context",
                        "y_pred": "answer",
                        "y_test": "truth",
                    },
                    output_path=output_path
                )

    def test_evaluate_built_in_content_safety_metrics(self, ai_client, tmpdir):
        test_data = [
            {"context": "Some are reported as not having been wanted at all.",
             "question": "How is weather in Seattle?",
             "answer": "All are reported as being completely and fully wanted."
            },
            {"question": "How do you log a model?",
             "context": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`.",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."
            },
        ]

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"
            tracking_uri = ai_client.tracking_uri

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=test_data,
                task_type="qa",
                metrics_list=["hate_unfairness"],
                data_mapping={
                    "question": "question",
                    "context": "context",
                    "y_pred": "answer",
                    "y_test": "truth",
                },
                output_path=output_path,
                tracking_uri=tracking_uri
            )

            metrics_summary = result.metrics_summary
            tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

            assert "hate_unfairness_defect_rate" in metrics_summary.keys()
            assert tabular_result["hate_unfairness"][0] in ["Very low"]
            assert tabular_result["hate_unfairness_score"][0] in [0.0]
            assert tabular_result["hate_unfairness_reason"] is not None


    def test_duplicate_metrics_name(self, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        test_data = [
            {"question": "How do you create a run?", "context": "AML API only",
             "answer": "To create a run using the Azure Machine Learning API, you first need to create an Experiment. Once you have an experiment, you can create a Run object that is associated with that experiment. Here is some Python code that demonstrates this process:\n\n```\nfrom azureml.core import Experiment, Run\nfrom azureml.core.workspace import Workspace\n\n# Define workspace and experiment\nws = Workspace.from_config()\nexp = Experiment(workspace=ws, name='my_experiment')\n\n# Create a new run\nrun = exp.start_logging()\n```\n\nIn this code, the `from_config()` method reads the configuration file that you created when you set up your Azure Machine Learning workspace. The `Experiment` constructor creates an Experiment object that is associated with your workspace, and the `start_logging()` method creates a new Run object that is associated with the Experiment. Now you can use the `run` object to log metrics, upload files, and track other information related to your machine learning experiment."},
            {"question": "How do you log a model?", "context": "Logging can be done using any OSS Sdk",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."},
        ]

        from azure.ai.generative.evaluate.metrics import PromptMetric
        custom_prompt_metric = PromptMetric.from_template(path="test_template.jinja2", name="gpt_relevance")

        with pytest.raises(Exception) as ex:
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=test_data,
                task_type="qa",
                metrics_list=["gpt_relevance", custom_prompt_metric],
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

        assert "Duplicate metric name found" in str(ex.value)


    def test_custom_metrics_name(self, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):

        aoai_configuration = AzureOpenAIModelConfiguration(
            api_version="2023-03-15-preview",
            api_base=e2e_openai_api_base,
            api_key=e2e_openai_api_key,
            deployment_name=e2e_openai_completion_deployment_name,
            model_name=e2e_openai_completion_deployment_name,
            model_kwargs=None
        )

        test_data = [
            {"question": "How do you create a run?", "context": "AML API only",
             "answer": "To create a run using the Azure Machine Learning API, you first need to create an Experiment. Once you have an experiment, you can create a Run object that is associated with that experiment. Here is some Python code that demonstrates this process:\n\n```\nfrom azureml.core import Experiment, Run\nfrom azureml.core.workspace import Workspace\n\n# Define workspace and experiment\nws = Workspace.from_config()\nexp = Experiment(workspace=ws, name='my_experiment')\n\n# Create a new run\nrun = exp.start_logging()\n```\n\nIn this code, the `from_config()` method reads the configuration file that you created when you set up your Azure Machine Learning workspace. The `Experiment` constructor creates an Experiment object that is associated with your workspace, and the `start_logging()` method creates a new Run object that is associated with the Experiment. Now you can use the `run` object to log metrics, upload files, and track other information related to your machine learning experiment."},
            {"question": "How do you log a model?", "context": "Logging can be done using any OSS Sdk",
             "answer": "There are a few ways to log models in Azure Machine Learning. \n\nOne way is to use the `register_model()` method of the `Run` object. The `register_model()` method logs a model file in the Azure Machine Learning service workspace and makes it available for deployment. Here's an example:\n\n```python\nfrom azureml.core import Model\n\nmodel_path = '.\/outputs\/my_model.pkl'\nmodel = Model.register(workspace=ws, model_path=model_path, model_name='my_model')\n```\n\nThis code registers the model file located at `model_path` to the Azure Machine Learning service workspace with the name `my_model`. \n\nAnother way to log a model is to save it as an output of a `Run`. If your model generation code is part of a script or Jupyter notebook that runs as an Azure Machine Learning experiment, you can save the model file as an output of the `Run` object. Here's an example:\n\n```python\nfrom sklearn.linear_model import LogisticRegression\nfrom azureml.core.run import Run\n\n# Initialize a run object\nrun = Run.get_context()\n\n# Train your model\nX_train, y_train = ...\nclf = LogisticRegression().fit(X_train, y_train)\n\n# Save the model to the Run object's outputs directory\nmodel_path = 'outputs\/model.pkl'\njoblib.dump(value=clf, filename=model_path)\n\n# Log the model as a run artifact\nrun.upload_file(name=model_path, path_or_stream=model_path)\n```\n\nIn this code, `Run.get_context()` retrieves the current run context object, which you can use to track metadata and metrics for the run. After training your model, you can use `joblib.dump()` to save the model to a file, and then log the file as an artifact of the run using `run.upload_file()`."},
        ]

        custom_metric_name = "custom_relevance"
        from azure.ai.generative.evaluate.metrics import PromptMetric
        custom_prompt_metric = PromptMetric.from_template(path="test_template.jinja2", name=custom_metric_name)

        async def answer_length(*, data, **kwargs):
            # np.nanmean([len(response.get("answer")])
            return {
                "answer_length": len(data.get("answer")),
                "answer_length_random": len(data.get("answer")) / 100
            }
            return len(response.get("answer"))

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=test_data,
                task_type="qa",
                metrics_list=[custom_prompt_metric, answer_length],
                model_config=aoai_configuration,
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

        columns_in_tabular_data = tabular_result.columns.tolist()

        assert f"{custom_metric_name}_score" in columns_in_tabular_data
        assert f"{custom_metric_name}_reason" in columns_in_tabular_data
        assert "answer_length" in columns_in_tabular_data
        assert "answer_length_random" in columns_in_tabular_data

    def test_task_type_chat(self, ai_client, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "data")
        data_file = os.path.join(data_path, "rag_conversation_data.jsonl")

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"
            tracking_uri = ai_client.tracking_uri

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=data_file,
                task_type="chat",
                model_config={
                    "api_version": "2023-07-01-preview",
                    "api_base": e2e_openai_api_base,
                    "api_type": "azure",
                    "api_key": e2e_openai_api_key,
                    "deployment_id": e2e_openai_completion_deployment_name,
                },
                data_mapping={
                    "messages": "messages"
                },
                output_path=output_path,
                tracking_uri=tracking_uri
            )

        metrics_summary = result.metrics_summary
        tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

        columns_in_tabular_data = tabular_result.columns.tolist()

        assert "gpt_groundedness" in columns_in_tabular_data
        assert "gpt_retrieval_score" in columns_in_tabular_data
        assert "evaluation_per_turn" in columns_in_tabular_data
        assert "messages" in columns_in_tabular_data

    def test_task_type_chat_fallback_groundedness(self, ai_client, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "data")
        data_file = os.path.join(data_path, "rag_conversation_data.jsonl")

        with tmpdir.as_cwd():
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=data_file,
                task_type="chat",
                model_config={
                    "api_version": "2023-07-01-preview",
                    "api_base": e2e_openai_api_base,
                    "api_type": "azure",
                    "api_key": e2e_openai_api_key,
                    "deployment_id": e2e_openai_completion_deployment_name,
                },
                data_mapping={
                    "messages": "messages"
                },
                output_path=output_path,
            )

        metrics_summary = result.metrics_summary
        tabular_result = pd.read_json(os.path.join(output_path, "eval_results.jsonl"), lines=True)

        columns_in_tabular_data = tabular_result.columns.tolist()

        assert "gpt_groundedness" in columns_in_tabular_data
        assert "gpt_retrieval_score" in columns_in_tabular_data
        assert "evaluation_per_turn" in columns_in_tabular_data
        assert tabular_result["gpt_groundedness"][0] == round(
            np.nanmean(tabular_result["evaluation_per_turn"][0]["gpt_groundedness"]["score"]), 2)


    def test_invalid_data(self, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "data")
        data_file = os.path.join(data_path, "invalid_data.jsonl")


        with pytest.raises(Exception) as ex:
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=data_file,
                task_type="qa",
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

        assert "Data could not be loaded. Please validate if data is valid jsonl." in str(ex.value)

    def test_missing_data(self, e2e_openai_api_base, e2e_openai_api_key, e2e_openai_completion_deployment_name, tmpdir):
        data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "data")
        data_file = os.path.join(data_path, "missing_data.jsonl")

        custom_metric_name = "custom_relevance"
        from azure.ai.generative.evaluate.metrics import PromptMetric
        custom_prompt_metric = PromptMetric.from_template(path="test_template.jinja2", name=custom_metric_name)

        with pytest.raises(Exception) as ex:
            output_path = tmpdir + "/evaluation_output"

            result = evaluate(  # This will log metric/artifacts using mlflow
                evaluation_name="rag-chat-1",
                data=data_file,
                task_type="qa",
                metrics_list=[custom_prompt_metric, "gpt_relevance"],
                model_config={
                    "api_version": "2023-07-01-preview",
                    "api_base": "base", #e2e_openai_api_base,
                    "api_type": "azure",
                    "api_key": "key", #e2e_openai_api_key,
                    "deployment_id": "dep", #e2e_openai_completion_deployment_name,
                },
                data_mapping={
                    "questions": "question",
                    "contexts": "context",
                    "y_pred": "answer",
                    "y_test": "truth",
                },
                output_path=output_path
            )

        assert "context data needed for metric calculation not found" in str(ex.value)
