# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import logging
import pathlib
import json
from typing import Dict, List
from .conversation_turn import ConversationTurn


logger = logging.getLogger(__file__)

class ConversationWriter:
    def __init__(self, file_path: pathlib.Path):
        self._file_path = file_path
        self._queue = asyncio.Queue()

    async def queue(self, conversation_id: str, conversation_history: List[ConversationTurn], meta_data=None):
        formatted_conversation = {
            "conversation_id": conversation_id,
            "conversation": [
                turn.to_annotation_format(turn_number=turn_number)
                for (turn_number, turn) in enumerate(conversation_history)],
        }
        if meta_data:
            formatted_conversation['meta_data'] = meta_data

        await self._queue.put(json.dumps(formatted_conversation) + "\n")

    def drain(self):
        logger.info(f"Draining {self._queue.qsize()} entries to {self._file_path.name}")
        with open(self._file_path, "a") as f:
            while not self._queue.empty():
                line = self._queue.get_nowait()
                f.write(line)
