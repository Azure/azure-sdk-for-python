# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Run a typed hosted text agent over the Voice Live bridge protocol."""

from azure.ai.agentserver.invocations.voice import (
    UserMessageEvent,
    VoiceAgentServerHost,
    VoiceResponse,
    VoiceSession,
)

app = VoiceAgentServerHost()


@app.on_user_message
async def on_user_message(
    session: VoiceSession,
    event: UserMessageEvent,
    response: VoiceResponse,
) -> None:
    """Return one complete text item; Voice Live synthesizes the audio."""
    del session
    await response.send_text(f"You said: {event.text}")


if __name__ == "__main__":
    app.run()
