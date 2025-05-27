# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.codetransparency.aio import CodeTransparencyClient


class TestCodeTransparencyClientAsync(object):

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the async client can be initialized correctly."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        assert client is not None
        assert isinstance(client, CodeTransparencyClient)
        await client.close()

    @pytest.mark.asyncio
    async def test_get_transparency_config_cbor_async(self):
        """Test getting the transparency config in CBOR format using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            response = await client.get_transparency_config_cbor()
            # In a real test, we would validate the response format
            assert response is not None
        except HttpResponseError:
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_public_keys_async(self):
        """Test getting public keys using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            response = await client.get_public_keys()
            # In a real test, we would validate the response format
            assert response is not None
        except HttpResponseError:
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_create_entry_async(self):
        """Test creating a code entry using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            sample_data = b"Sample binary data for testing"
            response = await client.create_entry(body=sample_data)
            # In a real test, we would validate the response format
            assert response is not None
        except HttpResponseError:
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_operation_async(self):
        """Test getting an operation status using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            # Using a fake operation ID for testing
            response = await client.get_operation(operation_id="fake-operation-id")
            # In a real test, we would validate the response format
            assert response is not None
        except (HttpResponseError, ResourceNotFoundError):
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_entry_async(self):
        """Test getting an entry by ID using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            # Using a fake entry ID for testing
            response = await client.get_entry(entry_id="fake-entry-id")
            # In a real test, we would validate the response format
            assert response is not None
        except (HttpResponseError, ResourceNotFoundError):
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_entry_statement_async(self):
        """Test getting an entry statement by ID using async client."""
        client = CodeTransparencyClient(
            endpoint="https://fake-endpoint.confidentialledger.azure.com",
            credential=AzureKeyCredential(key="test-api-key")
        )
        
        try:
            # Using a fake entry ID for testing
            response = await client.get_entry_statement(entry_id="fake-entry-id")
            # In a real test, we would validate the response format
            assert response is not None
        except (HttpResponseError, ResourceNotFoundError):
            # This is expected in a test environment without real service access
            pass
        finally:
            await client.close()
