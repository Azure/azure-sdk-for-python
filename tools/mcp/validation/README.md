# Azure SDK Validation Tools MCP Server

This is a Model Context Protocol (MCP) server that provides access to various validation and testing tools used in the Azure SDK for Python repository.

## Prerequisites

- Python 3.10 or higher
- uv
- tox
- Node

## Available Tools

This MCP server provides the following validation tools:

### verify_setup

Verifies Node, tox, and Python are installed in your environment.

### tox

Run tox environments. (e.g pylint, mypy, pyright)

## Tool Response Format

Each tool returns a response with the following structure:

```json
{
    "success": true/false,
    "stdout": "standard output from the command",
    "stderr": "standard error from the command",
    "code": 0,  // return code, 0 means success
    "error": "error message if any"
}
```
