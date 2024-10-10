# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import os
import sys


# Add parent directory to sys.path to import user_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from user_functions import fetch_current_datetime, fetch_weather, send_email
    

async def send_email_async(recipient: str, subject: str, body: str) -> str:
    await asyncio.sleep(1)    
    return send_email(recipient, subject, body)


# Statically defined user functions for fast reference with send_email as async but the rest as sync
user_async_functions = {"fetch_current_datetime": fetch_current_datetime, 
                  "fetch_weather": fetch_weather, 
                  "send_email": send_email_async
}
