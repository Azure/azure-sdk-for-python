# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
import uuid
from azure.communication.phonenumbers._generated.models import ReservationStatus


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
    
    def __init__(self, id: str, phone_numbers: dict):
        """Initialize a PhoneNumbersReservation object.

        :param id: The id of the reservation in GUID format.
        :type id: str
        :param phone_numbers: A dictionary containing the reservation phone numbers.
        :type phone_numbers: dict[str, ~azure.communication.phonenumbers.AvailablePhoneNumber]
        :raises ValueError: If the id is not in valid GUID format or if any required parameter is missing.
        """
        if id is None:
            raise ValueError("Parameter 'id' is required.")
            
        try:
            uuid.UUID(id)
        except ValueError:
            raise ValueError("The reservation id must be in valid GUID format")
        
        self.id = id
        self.phone_numbers = phone_numbers
        self.expires_at = None
        self.status = None

    @classmethod
    def _from_generated(cls, generated_reservation):
        """Creates a PhoneNumbersReservation object from a generated model.

        :param generated_reservation: The generated PhoneNumbersReservation model.
        :type generated_reservation: ~azure.communication.phonenumbers.models.PhoneNumbersReservation
        :return: A PhoneNumbersReservation object
        :rtype: ~azure.communication.phonenumbers.PhoneNumbersReservation
        """
        reservation = cls(
            id=generated_reservation.id,
            phone_numbers=generated_reservation.phone_numbers
        )
        reservation.expires_at = generated_reservation.expires_at
        reservation.status = generated_reservation.status
        return reservation


class PhoneNumbersReservationItem:
    def __init__(self, id: str, expires_at: datetime.datetime, status: ReservationStatus):
        self.id = id
        self.expires_at = expires_at
        self.status = status