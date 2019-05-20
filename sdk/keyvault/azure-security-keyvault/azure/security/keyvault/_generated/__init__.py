# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .v7_0 import models
from msrest.serialization import Deserializer, Serializer
from .key_vault_client_async import KeyVaultClientAsync

_CLIENT_MODELS = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
DESERIALIZE = Deserializer(_CLIENT_MODELS)
SERIALIZE = Serializer(_CLIENT_MODELS)

__all__ = ["KeyVaultClientAsync"]