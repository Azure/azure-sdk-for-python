# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE:browse_and_reserve_numbers_bulk_sample.py
DESCRIPTION:
    This sample demonstrates how to browse and reserve multiple phone numbers using your connection string and
    the Reservations API in the Azure Communication Phone Numbers SDK.
USAGE:
    python browse_and_reserve_numbers_bulk_sample.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
"""

import os
import uuid
from azure.communication.phonenumbers import PhoneNumbersClient

connection_str = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
phone_numbers_client = PhoneNumbersClient.from_connection_string(
    connection_str)


def browse_and_reserve_numbers_bulk():
    # Browse for geographic phone numbers in the US using specific area codes.
    area_codes = ["212", "718", "917"]
    browse_result = phone_numbers_client.browse_available_phone_numbers(
        country_code="US",
        phone_number_type="geographic",
        phone_number_prefixes=area_codes
    )
    # Reserve 3 phone numbers from the browse result.
    numbers_to_reserve = browse_result.phone_numbers[:3]
    print(f"Reserving phone numbers: {[n.id for n in numbers_to_reserve]}")

    # The reservation ID needs to be a valid UUID.
    reservation_id = str(uuid.uuid4())
    print(f"Using reservation ID: {reservation_id}")

    reservation = phone_numbers_client.create_or_update_reservation(
        reservation_id=reservation_id,
        numbers_to_add=numbers_to_reserve
    )

    # Check if any errors occurred during reservation
    numbers_with_error = [
        n for n in reservation.phone_numbers.values() if n.status == "error"]
    if any(numbers_with_error):
        print("Errors occurred during reservation:")
        for number in numbers_with_error:
            print(
                f"Phone number: {number.phone_number}, Error: {number.error.code}, Message: {number.error.message}")
    else:
        print("Reservation operation completed without errors.")

    # Clean up the reservation after use
    print(f"Deleting reservation with ID: {reservation_id}")
    phone_numbers_client.delete_reservation(reservation_id=reservation_id)
    print("Reservation deleted successfully.")


if __name__ == "__main__":
    browse_and_reserve_numbers_bulk()
