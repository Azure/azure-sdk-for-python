# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates authenticating a client via:
        * api key
        * Azure Active Directory(AAD)

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running this sample:
    1) FACE_ENDPOINT - the endpoint to your Face resource.
    The environment variable below is used for api key authentication.
    2) FACE_KEY - your Face API key.
    The following environment variables are required for using azure-identity's DefaultAzureCredential.
    For more information, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
    3) AZURE_TENANT_ID - the tenant ID in Azure Active Directory
    4) AZURE_CLIENT_ID - the application (client) ID registered in the AAD tenant
    5) AZURE_CLIENT_SECRET - the client secret for the registered application
"""
import os

from dotenv import find_dotenv, load_dotenv

from _shared.constants import (
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    DEFAULT_FACE_API_ACCOUNT_KEY,
    DEFAULT_FACE_API_ENDPOINT,
    DEFAULT_IMAGE_FILE,
)
from _shared.helpers import beautify_json, get_logger


class FaceAuthentication():
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT)
        self.key = os.getenv(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY)
        self.logger = get_logger("sample_authentication")

    def authentication_by_api_key(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        self.logger.info("Instantiate a FaceClient using an api key")
        with FaceClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as face_client:
            from pathlib import Path

            sample_file_path = Path(__file__).resolve().parent / DEFAULT_IMAGE_FILE
            with open(sample_file_path, "rb") as fd:
                file_content = fd.read()

            result = face_client.detect(
                file_content,
                FaceDetectionModel.DETECTION_03,
                FaceRecognitionModel.RECOGNITION_04,
                False)

            self.logger.info(f"Detect faces from the file: {sample_file_path}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")

    def authentication_by_aad_credential(self):
        from azure.identity import DefaultAzureCredential
        from azure.ai.vision.face import FaceClient
        from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

        self.logger.info("Instantiate a FaceClient using a TokenCredential")
        with FaceClient(endpoint=self.endpoint, credential=DefaultAzureCredential()) as face_client:
            from pathlib import Path

            sample_file_path = Path(__file__).resolve().parent / DEFAULT_IMAGE_FILE
            with open(sample_file_path, "rb") as fd:
                file_content = fd.read()

            result = face_client.detect(
                file_content,
                FaceDetectionModel.DETECTION_03,
                FaceRecognitionModel.RECOGNITION_04,
                False)

            self.logger.info(f"Detect faces from the file: {sample_file_path}")
            for idx, face in enumerate(result):
                self.logger.info(f"----- Detection result: #{idx+1} -----")
                self.logger.info(f"Face: {beautify_json(face.as_dict())}")


if __name__ == "__main__":
    sample = FaceAuthentication()
    sample.authentication_by_api_key()
    sample.authentication_by_aad_credential()
