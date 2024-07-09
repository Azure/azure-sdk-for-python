# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import fastapi
import uvicorn

from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure monitor collection telemetry pipeline
configure_azure_monitor()

app = fastapi.FastAPI()


# Requests made to fastapi endpoints will be automatically captured
@app.get("/")
async def test():
    return {"message": "Hello World"}


# Exceptions that are raised within the request are automatically captured
@app.get("/exception")
async def exception():
    raise Exception("Hit an exception")


# Set the OTEL_PYTHON_EXCLUDE_URLS environment variable to "http://127.0.0.1:8000/exclude"
# Telemetry from this endpoint will not be captured due to excluded_urls config above
@app.get("/exclude")
async def exclude():
    return {"message": "Telemetry was not captured"}


if __name__ == "__main__":
    # cSpell:disable
    uvicorn.run("http_fastapi:app", port=8008, reload=True)
    # cSpell:disable
