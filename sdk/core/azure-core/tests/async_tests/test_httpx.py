import httpx
import aiohttp
import pytest



@pytest.mark.asyncio
async def test_normal_call():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:5000/basic/string")
        response.raise_for_status()
        raise ValueError(response.text)