# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# import asyncio
# import logging

# from azure.ai.agentserver.responses import (
#     CreateResponse,
#     ResponseContext,
#     ResponsesAgentServerHost,
#     TextResponse,
# )

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# app = ResponsesAgentServerHost()


# @app.create_handler
# async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
#     """Echo the user's input back as a single message."""
#     input_text = await context.get_input_text()
#     logger.info(f"Received input: {input_text}")

#     output_text = f"Echo: {input_text}"
#     logger.info(f"Sending output: {output_text}")

#     return TextResponse(context, request, text=output_text)


# def main() -> None:
#     app.run()


# if __name__ == "__main__":
#     main()
