# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_face_liveness_detection_with_verification_async.py

DESCRIPTION:
    This sample demonstrates how to determine if a face in an input video stream is real (live) or fake (spoof), and
    verify if the face belongs to the particular person.

    The liveness solution integration involves two different components: a mobile application and
    an app server/orchestrator, and here we demonstrate the entire process from the perspective of the server side.

    For more information about liveness detection, see
    https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness.

USAGE:
    python sample_face_liveness_detection_with_verification_async.py

    Set the environment variables with your own values before running this sample:
    1) AZURE_FACE_API_ENDPOINT - the endpoint to your Face resource.
    2) AZURE_FACE_API_ACCOUNT_KEY - your Face API key.
"""
import asyncio
import os
import uuid

from dotenv import find_dotenv, load_dotenv

from shared.constants import (
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    DEFAULT_FACE_API_ACCOUNT_KEY,
    DEFAULT_FACE_API_ENDPOINT,
    TestImages,
)
from shared import helpers
from shared.helpers import beautify_json, get_logger


class DetectLivenessWithVerify:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.getenv(
            CONFIGURATION_NAME_FACE_API_ENDPOINT, DEFAULT_FACE_API_ENDPOINT
        )
        self.key = os.getenv(
            CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY, DEFAULT_FACE_API_ACCOUNT_KEY
        )
        self.logger = get_logger(
            "sample_face_liveness_detection_with_verification_async"
        )

    async def wait_for_liveness_check_request(self):
        # The logic to wait for liveness check request from mobile application.
        pass

    async def send_auth_token_to_client(self, token):
        # The logic to provide the session-authorization-token to the mobile application.
        pass

    async def wait_for_liveness_session_complete(self):
        # The logic to wait the notification from mobile application.
        self.logger.info(
            "Please refer to https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness"
            " and use the mobile client SDK to perform liveness detection on your mobile application."
        )
        input(
            "Press any key to continue when you complete these steps to run sample to get session results ..."
        )
        pass

    async def livenessSessionWithVerify(self):
        """This example demonstrates the liveness detection with face verification from a app server-side perspective.
        To get the full picture of the entire steps, see https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness#perform-liveness-detection-with-face-verification  # noqa: E501
        """
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.vision.face.aio import FaceSessionClient
        from azure.ai.vision.face.models import (
            CreateLivenessSessionContent,
            LivenessOperationMode,
        )

        async with FaceSessionClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as face_session_client:
            # 1. Wait for liveness check request
            await self.wait_for_liveness_check_request()

            # 2. Create a session with verify image.
            verify_image_file_path = helpers.get_image_path(
                TestImages.DEFAULT_IMAGE_FILE
            )

            self.logger.info(
                "Create a new liveness with verify session with verify image."
            )
            created_session = await face_session_client.create_liveness_with_verify_session(
                CreateLivenessSessionContent(
                    liveness_operation_mode=LivenessOperationMode.PASSIVE,
                    device_correlation_id=str(uuid.uuid4()),
                    send_results_to_client=False,
                    auth_token_time_to_live_in_seconds=60,
                ),
                verify_image=helpers.read_file_content(verify_image_file_path),
            )
            self.logger.info(f"Result: {beautify_json(created_session.as_dict())}")

            # 3. Provide session authorization token to mobile application.
            token = created_session.auth_token
            await self.send_auth_token_to_client(token)

            # 4 ~ 6. The mobile application uses the session-authorization-token to perform the liveness detection.
            # To learn how to integrate the UI and the code into your native mobile application, see
            # https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness#integrate-liveness-into-mobile-application  # noqa: E501

            # 7. Wait for session completion notification from client.
            await self.wait_for_liveness_session_complete()

            # 8. Query for the liveness detection result as the session is completed.
            self.logger.info("Get the liveness detection result.")
            liveness_result = (
                await face_session_client.get_liveness_with_verify_session_result(
                    created_session.session_id
                )
            )
            self.logger.info(f"Result: {beautify_json(liveness_result.as_dict())}")

            # Furthermore, you can query all request and response for this sessions, and list all sessions you have by
            # calling `get_liveness_session_audit_entries` and `get_liveness_sessions`.
            self.logger.info("Get the audit entries of this session.")
            audit_entries = await face_session_client.get_liveness_with_verify_session_audit_entries(
                created_session.session_id
            )
            for idx, entry in enumerate(audit_entries):
                self.logger.info(f"----- Audit entries: #{idx+1}-----")
                self.logger.info(f"Entry: {beautify_json(entry.as_dict())}")

            self.logger.info("List all liveness sessions.")
            sessions = await face_session_client.get_liveness_sessions()
            for idx, session in enumerate(sessions):
                self.logger.info(f"----- Sessions: #{idx+1}-----")
                self.logger.info(f"Session: {beautify_json(session.as_dict())}")

            # Clean up: Delete the session
            self.logger.info("Delete the session.")
            await face_session_client.delete_liveness_with_verify_session(
                created_session.session_id
            )


async def main():
    sample = DetectLivenessWithVerify()
    await sample.livenessSessionWithVerify()


if __name__ == "__main__":
    asyncio.run(main())
