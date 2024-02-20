# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
import os
from typing import Union, Optional
import uuid

import yaml  # type: ignore[import]

from azure.ai.resources.entities.models import Model


CHAT_SCORING_SCRIPT_TEMPLATE = '''
import asyncio
import json
import os
from pathlib import Path
from inspect import iscoroutinefunction
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
    resolved_path = str(Path(os.getenv("AZUREML_MODEL_DIR")).resolve() / "{}")
    sys.path.append(resolved_path)

@rawhttp
def run(raw_data: AMLRequest):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    raw_data = json.loads(raw_data.data)
    messages = raw_data["messages"]
    messages = [
        {{
            "role": message["role"],
            "content": message["content"], 
        }} 
        for message in messages if message.get("kind", "text") == "text"
    ]
    stream = raw_data.get("stream", False)
    session_state = raw_data.get("sessionState", raw_data.get("session_state", None))
    context = raw_data.get("context", {{}})
    from {} import chat_completion
    if iscoroutinefunction(chat_completion):
        response = asyncio.run(
            chat_completion(
                messages,
                stream,
                session_state,
                context,
            )
        )
    else:
        response = chat_completion(
            messages,
            stream,
            session_state,
            context,
        )
    if stream:
        aml_response = AMLResponse(response_to_dict(response), 200)
        aml_response.headers["Content-Type"] = "application/jsonl"
        return aml_response
    return json.loads(json.dumps(response))

'''


def create_chat_scoring_script(
    directory: Union[str, os.PathLike],
    chat_module: str,
    model_dir_name: Optional[str] = None,
) -> None:
    score_file_path = f"{str(directory)}/score.py"
    with open(score_file_path, "w+") as f:
        f.write(CHAT_SCORING_SCRIPT_TEMPLATE.format(model_dir_name if model_dir_name else "", chat_module))


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
