# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
import os
from typing import Union
import uuid

import yaml

from azure.ai.resources.entities.models import Model


CHAT_SCORING_SCRIPT_TEMPLATE = '''
import asyncio
import json
import os
from pathlib import Path
import sys
from azureml.contrib.services.aml_request import AMLRequest, rawhttp
from azureml.contrib.services.aml_response import AMLResponse
import json
import importlib


def response_to_dict(response):
    for resp in response:
        yield json.dumps(resp) + \"\\n\"

def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # Please provide your model's folder name if there is one
    print(os.getenv("AZUREML_MODEL_DIR"))
    resolved_path = str(Path(os.getenv("AZUREML_MODEL_DIR")).resolve())
    sys.path.append(resolved_path)

@rawhttp
def run(raw_data: AMLRequest):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    raw_data = json.loads(raw_data.data)
    stream = raw_data["stream"]
    from {} import chat_completion
    response = asyncio.run(chat_completion(**raw_data))
    if stream:
        aml_response = AMLResponse(response_to_dict(response), 200)
        aml_response.headers["Content-Type"] = "text/event-stream"
        return aml_response
    return json.dumps(response)

'''


def create_chat_scoring_script(
    directory: Union[str, os.PathLike],
    chat_module: str,
) -> None:
    score_file_path = f"{str(directory)}/score.py"
    with open(score_file_path, "w+") as f:
        f.write(CHAT_SCORING_SCRIPT_TEMPLATE.format(chat_module))


def create_mlmodel_file(model: Model):
    with open(f"{model.path}/MLmodel", "w+") as f:
        now = datetime.datetime.utcnow()
        mlmodel_dict = {
            "flavors": {
                "python_function": {
                    "code": ".",
                    "data": ".",
                    "env": model.conda_file,
                    "loader_module": model.loader_module
                }
            },
            "model_uuid": str(uuid.uuid4()).replace("-", ""),
            "utc_time_created": now.strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        yaml.safe_dump(mlmodel_dict, f)
