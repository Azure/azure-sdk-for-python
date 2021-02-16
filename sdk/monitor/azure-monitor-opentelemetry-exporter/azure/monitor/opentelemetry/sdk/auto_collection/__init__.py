# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
from azure.monitor.opentelemetry.sdk.auto_collection._auto_collection import (
    AutoCollection,
    standard_metrics_processor
)

__all__ = ["AutoCollection", "standard_metrics_processor"]
