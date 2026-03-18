"""Minimal agent — no SDK required.

Implements only the required ``POST /invocations`` endpoint.
See SPEC.md for the full Invocation API contract.

Usage::

    pip install fastapi uvicorn
    python minimal_server.py

    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/invocations")
async def invoke(request: Request):
    data = await request.json()
    greeting = f"Hello, {data.get('name', 'Alice')}!"
    return JSONResponse({"greeting": greeting})


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("AGENT_SERVER_PORT", "8088"))
    uvicorn.run(app, host="0.0.0.0", port=port)
