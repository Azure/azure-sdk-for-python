# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Shared credential redaction for sample capture and live sample log files."""

import os
import re

MAX_LOG_CHARACTERS = 8 * 1024 * 1024
_SECRET_NAMES = (
    r"authorization|proxy-authorization|x-api-key|api[-_]?key|ocp-apim-subscription-key|"
    r"access[-_]?token|refresh[-_]?token|id[-_]?token|client[-_]?secret|password|"
    r"accountkey|sharedaccesssignature|cookie|set-cookie"
)


def sanitize_log(text: str) -> str:
    """Redact credential-shaped fields and known secret environment values."""
    secrets = {
        value
        for name, value in os.environ.items()
        if len(value) >= 8
        and name != "AZURE_TOKEN_CREDENTIALS"
        and re.search(r"(?i)secret|password|token|(?:^|_)pat(?:_|$)|(?:^|_)key(?:_|$)|connection_string", name)
    }
    for value in sorted(secrets, key=len, reverse=True):
        text = text.replace(value, "<REDACTED>")
    text = re.sub(r"\b(?:github_pat_[A-Za-z0-9_]+|gh[opusr]_[A-Za-z0-9]+)\b", "<REDACTED>", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "<REDACTED>", text)
    text = re.sub(r"(?i)\b(Bearer|Basic)\s+[^\s\"',;<>]+", r"\1 <REDACTED>", text)
    text = re.sub(rf'(?i)("(?:{_SECRET_NAMES})"\s*:\s*)"(?:\\.|[^"\\])*"', r'\1"<REDACTED>"', text)
    text = re.sub(rf"(?i)('(?:{_SECRET_NAMES})'\s*:\s*)'(?:\\.|[^'\\])*'", r"\1'<REDACTED>'", text)
    text = re.sub(rf"(?im)^([ \t]*(?:{_SECRET_NAMES})[ \t]*:[ \t]*).*$", r"\1<REDACTED>", text)
    text = re.sub(rf"(?i)(\b(?:{_SECRET_NAMES})=)[^;\s&\"'<>]+", r"\1<REDACTED>", text)
    text = re.sub(
        r"(?i)([?&](?:sig|token|access_token|api[-_]?key|key|code|client_secret)=)[^&\s\"'<>]+",
        r"\1<REDACTED>",
        text,
    )
    return re.sub(r"(https?://)[^\s/@:]+:[^\s/@]+@", r"\1<REDACTED>@", text)


def write_log_file(path: str, text: str) -> None:
    """Sanitize the entire formatted log, including prints and exceptions, before writing."""
    content = (
        sanitize_log(text)
        if len(text) <= MAX_LOG_CHARACTERS
        else "Log omitted because it exceeds the safe sample log size limit.\n"
    )
    with open(path, "w", encoding="utf-8") as log_file:
        log_file.write(content)
