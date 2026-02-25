# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
This is a sample Azure Function app used by sample_agent_azure_function.py
to demonstrate how to integrate Azure Functions with AI Agents using queue triggers.
"""

# import azure.functions as func
# import logging
# import json

# app = func.FunctionApp()

# @app.queue_trigger(arg_name="msg", queue_name="input", connection="STORAGE_CONNECTION")
# @app.queue_output(arg_name="outputQueue", queue_name="output", connection="STORAGE_CONNECTION")
# def queue_trigger(msg: func.QueueMessage, outputQueue: func.Out[str]):
#     try:
#         messagepayload: dict = json.loads(msg.get_body().decode("utf-8"))
#         logging.info(f"The function receives the following message: {json.dumps(messagepayload)}")

#         function_args: dict = messagepayload.get("function_args", {})
#         location: str = function_args.get("location")


#         weather_result = f"Weather is {len(location)} degrees and sunny in {location}"
#         response_message = {
#             "Value": weather_result,
#             "CorrelationId": messagepayload["CorrelationId"]
#         }
#         logging.info(f"The function returns the following message through the {outputQueue} queue: {json.dumps(response_message)}")

#         outputQueue.set(json.dumps(response_message))

#     except Exception as e:
#         logging.error(f"Error processing message: {e}")
