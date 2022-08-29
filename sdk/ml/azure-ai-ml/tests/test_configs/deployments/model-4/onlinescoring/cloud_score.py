import os
import logging
import json
import numpy
import joblib
from sklearn.linear_model import Ridge


def init():
    global model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model/model.pkl")
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    logging.info("Init complete")


# note you can pass in multiple rows for scoring
def run(raw_data):
    try:
        logging.info("Request received")
        data = json.loads(raw_data)["data"]
        data = numpy.array(data)
        result = model.predict(data)
        logging.info("Request processed")
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error
