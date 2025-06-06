# Azure SDK Validation Tools MCP Server

This is a Model Context Protocol (MCP) server that provides access to various validation and testing tools used in the Azure SDK for Python repository.

## Prerequisites

- Python 3.10 or higher
- uv
- tox
- Node.js

## Available Tools

This MCP server provides the following validation tools:

### verify_setup

Verifies Node.js, tox, and Python are installed in your environment.

### tox

Run tox environments. (e.g pylint, mypy, pyright)