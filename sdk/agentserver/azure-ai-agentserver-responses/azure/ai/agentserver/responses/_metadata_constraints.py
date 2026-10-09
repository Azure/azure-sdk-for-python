# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Shared constraints for Responses metadata."""

# These limits are defined by the Responses Metadata contract generated in
# models._generated.types.Metadata. Keep runtime validation centralized here
# so a future contract revision requires one implementation change.
MAX_METADATA_KEYS = 16
MAX_METADATA_KEY_LENGTH = 64
MAX_METADATA_VALUE_LENGTH = 512
