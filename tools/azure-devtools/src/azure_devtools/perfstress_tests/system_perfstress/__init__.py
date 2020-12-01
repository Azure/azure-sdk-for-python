# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

try:
    import aiohttp
    import httpx
    import requests
    import tornado
except ImportError as e:
    message = "Cannot load systemperf dependencies. Please install as 'azure-devtools[systemperf]'."
    raise ImportError(message) from e
