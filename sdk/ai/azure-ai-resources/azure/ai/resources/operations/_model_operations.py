# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import subprocess
from pathlib import Path
from typing import Union


from azure.ai.ml import MLClient
from azure.ai.resources.entities.models import Model, PromptflowModel
from azure.ai.resources._utils._dockerfile_utils import create_dockerfile
from azure.ai.resources._utils._scoring_script_utils import create_mlmodel_file


class ModelOperations():
    def __init__(
        self,
        ml_client: MLClient,
        **kwargs
    ):
        self._ml_client = ml_client

    def package(
        self,
        model: Union[Model, PromptflowModel],
        output: Union[str, os.PathLike]=Path.cwd()
    ) -> None:
        output_path = Path(output/"model_package")
        output_path.mkdir(exist_ok=True)
        if isinstance(model, Model):
            if model.chat_module and model.loader_module:
                raise Exception("Only one of chat_module or loader_module can be provided to Model")
            if model.chat_module:
                # create custom model dockerfile
                create_dockerfile(model, output_path, "chat")
            elif model.loader_module:
                # create mlflow dockerfile
                create_mlmodel_file(model)
                create_dockerfile(model, output_path, "mlflow")
            elif "MLmodel" in [path for path in os.listdir(model.path)]:
                create_dockerfile(model, output_path, "mlflow")
            else:
                raise Exception("Either one of chat_module or loader_module must be provided to Model if MLmodel is not present in Model.path ")
        elif isinstance(model, PromptflowModel):
            try:
                import promptflow
            except ImportError as e:
                print('In order to create a package for a promptflow, please make sure the promptflow SDK is installed in your environment')
                raise e
            # hack since pf build under the hood uses multi-processing to create new process. Due to implementation differences between
            # windows and linux of creating a new process, we cannot use the SDK function directly and instead need to use the CLI
            # in a separate process
            subprocess.call(["pf", "flow", "build", "--source", model.path, "--output", output_path, "--format", "docker"])
        else:
            raise Exception("Passed in model is not supported for packaging")
