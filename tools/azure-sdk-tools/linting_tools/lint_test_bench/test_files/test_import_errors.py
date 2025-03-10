# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import requests
import httpx
import aiohttp
from azure.core.exceptions import raise_with_traceback
# This code violates no-raise-with-traceback, networking-import-outside-azure-core-transport


async def main():
    r = requests.get("http://localhost:8080/basic/string", timeout=0.1)
    print(r.status_code)
    r = httpx.get("http://localhost:8080/basic/string")
    print(r.status_code)
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/basic/string") as response:
            print(response.status)

    l = {}
    try:
        l["a"].append(1)
    except TypeError:
        print("An error occurred")
        raise_with_traceback(ValueError("This is a test error"))
