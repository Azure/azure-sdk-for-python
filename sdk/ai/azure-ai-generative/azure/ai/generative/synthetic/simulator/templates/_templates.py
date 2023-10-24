# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

CONVERSATION_PATH = "user.md"
SUMMARIZATION_PATH = "summarization.md"
SEARCH_PATH = "search.md"

CONVERSATION = "conversation"
SUMMARIZATION = "summarization"
SEARCH = "search"

CONTEXT_KEY = {
    "conversation": ["metadata"],
    "summarization": ["file_content"],
    "search": []
}

CONVERSATION_CONTEXT_KEY = ["metadata"]
SUMMARIZATION_CONTEXT_KEY = [""]

ALL_TEMPLATES = {
    "conversation": CONVERSATION_PATH,
    "summarization": SUMMARIZATION_PATH,
    "search": SEARCH_PATH
}
