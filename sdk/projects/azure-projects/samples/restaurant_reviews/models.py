# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Literal, Optional
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, AliasChoices


class Restaurant(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        serialization_alias="PartitionKey",
        validation_alias=AliasChoices("id", "PartitionKey"),
    )
    name: str = Field(serialization_alias="RowKey", validation_alias=AliasChoices("name", "RowKey"))
    street_address: str
    description: Optional[str]


class Review(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        serialization_alias="PartitionKey",
        validation_alias=AliasChoices("id", "PartitionKey"),
    )
    restaurant: str = Field(serialization_alias="RowKey", validation_alias=AliasChoices("restaurant", "RowKey"))
    user_name: str
    rating: int
    review_text: str
    review_date: datetime
