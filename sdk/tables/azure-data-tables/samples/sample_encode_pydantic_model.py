# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_encode_pydantic_model.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities into a table
    and deleting entities from a table.

USAGE:
    python sample_encode_pydantic_model.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import os
from typing import Literal, Optional
from datetime import datetime, timezone
from uuid import uuid4
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, AliasChoices
from azure.data.tables import TableClient, EdmType


class Review(BaseModel):
    user_name: str
    rating: int
    review_text: Optional[str] = None
    review_date: datetime


class Restaurant(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        serialization_alias="PartitionKey",
        validation_alias=AliasChoices("id", "PartitionKey"),
    )
    name: str = Field(serialization_alias="RowKey", validation_alias=AliasChoices("name", "RowKey"))
    street_address: str
    description: Optional[str] = None
    review: Review


def encode_review(value):
    return EdmType.STRING, str(value)


encoder_map = {
    dict: encode_review,
}


class CreateDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "CustomEncoderPydanticModel"

    def create_delete_entity(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name, encoder_map=encoder_map
        )
        with table_client:
            table_client.create_table()

            review = Review(
                user_name="Alex",
                rating=8,
                review_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
            )
            restaurant = Restaurant(
                name="Cafe1",
                street_address="One Microsoft Way, Redmond, WA, 98052",
                review=review,
            )
            entity = restaurant.model_dump(by_alias=True)

            result = table_client.create_entity(entity=entity)
            print(f"Created entity: {result}")

            result = table_client.get_entity(entity["PartitionKey"], entity["RowKey"])
            print(f"Get entity result: {result}")

            table_client.delete_entity(entity=entity)
            print("Successfully deleted!")

            table_client.delete_table()
            print("Cleaned up")


if __name__ == "__main__":
    ide = CreateDeleteEntity()
    ide.create_delete_entity()
