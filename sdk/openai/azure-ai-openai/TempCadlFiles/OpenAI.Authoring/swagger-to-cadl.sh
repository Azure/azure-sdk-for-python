#!/bin/bash
autorest --reset
autorest --require=README.md --cadl-init --use=https://aka.ms/autorest.cadl --output-folder="." --input-file="https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/authoring/preview/2022-06-01-preview/azureopenai.json"