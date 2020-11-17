# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_orders_sample_async.py
DESCRIPTION:
    This sample demonstrates how to list, acquire and cancel phone number orders via a connection string,
    reservation id, phone plan id and and area code.
USAGE:
    python phone_number_orders_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RELEASE_ID - The release id you want to get info from
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID - The reservation id you want to get info from
    4) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_RESERVATION - The area code to create reservation
    5) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID - The phone plan id
    6) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID_TO_PURCHASE - The reservation id you want to purchase
    7) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID_TO_CANCEL - The reservation id you want to cancel
"""

import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import CreateSearchOptions

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
release_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RELEASE_ID', "release-id")
reservation_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID', "reservation-id")
area_code_for_reservation = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_RESERVATION', "area-code")
phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")
reservation_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID_TO_PURCHASE',
                                       "reservation-id")
reservation_id_to_cancel = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RESERVATION_ID_TO_CANCEL',
                                     "reservation-id")


async def get_release_by_id():
    # [START get_release_by_id]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_number_release_response = await phone_number_administration_client.get_release_by_id(
            release_id=release_id
        )
        print('phone_number_release_response:')
        print(phone_number_release_response)
    # [END get_release_by_id]


async def list_all_releases():
    # [START list_all_releases]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        releases_response = phone_number_administration_client.list_all_releases()
        print('releases_response:')
        async for release in releases_response:
            print(release)
    # [END list_all_releases]


async def get_reservation_by_id():
    # [START get_reservation_by_id]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_number_reservation_response = await phone_number_administration_client.get_reservation_by_id(
            reservation_id=reservation_id
        )
        print('phone_number_reservation_response:')
        print(phone_number_reservation_response)
    await phone_number_administration_client.close()
    # [END get_reservation_by_id]


async def begin_reserve_phone_numbers():
    # [START begin_reserve_phone_numbers]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    reservationOptions = CreateSearchOptions(
        area_code=area_code_for_reservation,
        description="testreservation20200014",
        display_name="testreservation20200014",
        phone_plan_ids=[phone_plan_id],
        quantity=1
    )
    async with phone_number_administration_client:
        reserve_phone_numbers_response = await phone_number_administration_client.begin_reserve_phone_numbers(
            options=reservationOptions
        )
        print('reserve phone numbers status:')
        print(reserve_phone_numbers_response.status())
    # [END begin_reserve_phone_numbers]


async def cancel_reservation():
    # [START cancel_reservation]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        await phone_number_administration_client.cancel_reservation(
            reservation_id=reservation_id_to_cancel
        )
    # [END cancel_reservation]


async def begin_purchase_reservation():
    # [START begin_purchase_reservation]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        await phone_number_administration_client.begin_purchase_reservation(
            reservation_id=reservation_id_to_purchase
        )
    # [END begin_purchase_reservation]


async def main():
    await get_release_by_id()
    await list_all_releases()
    await get_reservation_by_id()
    await begin_reserve_phone_numbers()
    await cancel_reservation()
    # await begin_purchase_reservation() #currently throws error if purchase an already purchased number

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
