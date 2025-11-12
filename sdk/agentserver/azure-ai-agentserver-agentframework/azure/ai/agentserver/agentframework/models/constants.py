# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class Constants:
    # streaming configuration
    # Environment variable name to control idle timeout for streaming updates (seconds)
    AGENTS_ADAPTER_STREAM_TIMEOUT_S = "AGENTS_ADAPTER_STREAM_TIMEOUT_S"
    # Default idle timeout (seconds) when env var or request override not provided
    DEFAULT_STREAM_TIMEOUT_S = 300.0

    # model defaults
    DEFAULT_TEMPERATURE = 1.0
    DEFAULT_TOP_P = 1.0
