# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
import uuid
from azure.communication.phonenumbers._generated.models import ReservationStatus, AvailablePhoneNumber


class PhoneNumbersReservation:
    """Represents a reservation for phone numbers. A reservation is a temporary hold on phone numbers
    that can later be purchased. The reservation has a limited lifetime after which the phone
    numbers are released if not purchased. Reservations older than 1 month are automatically
    deleted.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The id of the reservation.
    :vartype id: str
    :ivar expires_at: The time at which the reservation will expire. If a reservation is not
     purchased before this time, all of the reserved phone numbers will be released and made
     available for others to purchase.
    :vartype expires_at: ~datetime.datetime
    :ivar phone_numbers: A dictionary containing the reservation phone numbers. The key is the ID
     of the phone number (digits only) and values are AvailablePhoneNumber objects. Not populated
     when retrieving PhoneNumbersReservation collections.
    :vartype phone_numbers: dict[str,
      ~azure.communication.phonenumbers.AvailablePhoneNumber]
    :ivar status: Represents the status of the reservation. Possible values include: 'active',
     'submitted', 'completed', 'expired'. Known values are: "active", "submitted", "completed", and
     "expired".
    :vartype status: str or ~azure.communication.phonenumbers.ReservationStatus
    """

    def __init__(self, id: str, **kwargs):
        """Initialize a PhoneNumbersReservation object.

        :param id: The id of the reservation in GUID format.
        :type id: str
        :raises ValueError: If the id is not in valid GUID format or if any required parameter is missing.
        """
        if id is None:
            raise ValueError("Parameter 'id' is required.")

        try:
            uuid.UUID(id)
        except ValueError as exc:
            raise ValueError(
                "The reservation id must be in valid GUID format") from exc

        self.id = id

        # These properties are not intended to be set by the user,
        # but they are used when mapping from the generated model.
        self.expires_at = kwargs.get("expires_at", None)
        self.status = kwargs.get("status", None)
        self.phone_numbers = kwargs.get("phone_numbers", {})

    def add_phone_number(self, available_phone_number: AvailablePhoneNumber):
        """Adds a phone number to the reservation. 

        :param available_phone_number: The phone number to add to the reservation.
        :type available_phone_number: ~azure.communication.phonenumbers.AvailablePhoneNumber
        """
        if not isinstance(available_phone_number, AvailablePhoneNumber):
            raise ValueError(
                "The phone number must be an instance of AvailablePhoneNumber")

        phone_number_id = None
        if available_phone_number.id:
            phone_number_id = available_phone_number.id
        else:
            phone_number_id = available_phone_number.phone_number

        if phone_number_id is None:
            raise ValueError("The phone number id is required.")

        self.phone_numbers[phone_number_id] = available_phone_number

    def remove_phone_number(self, phone_number_id: str):
        """Removes a phone number from the reservation.

        :param phone_number_id: The ID of the phone number to remove from the reservation.
        :type phone_number_id: str
        """
        self.phone_numbers[phone_number_id] = None


class PhoneNumbersReservationItem:
    def __init__(self, id: str, expires_at: datetime.datetime, status: ReservationStatus):
        self.id = id
        self.expires_at = expires_at
        self.status = status
