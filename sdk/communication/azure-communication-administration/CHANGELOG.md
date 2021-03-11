# Release History

## 1.0.0b4 (2020-20-09)

### Breaking Changes
- CommunicationIdentityClient is moved to a new package: "azure.communication.identity".
- Replaced CommunicationUser with CommunicationUserIdentifier.
- Renamed CommunicationUserCredential to CommunicationTokenCredential.


##### `PhoneNumberAdministrationClient`
-  `begin_reserve_phone_numbers` now takes `display_name`, `description`, `phone_plan_ids`, 
`area_code`, `quantity`, `location_options`, or `continuation_token` keywords as input. 
Caller must provide one of the following:
 (1) all of keywords `display_name`, `description`, `phone_plan_ids`, `area_code`, `quantity` if all the phone plans
 to reserve are toll-free plans.
 (2) all of keywords `display_name`, `description`, `phone_plan_ids`, `area_code`, `quantity`, `location_options`
 if at least one phone plan to reserve is not toll-free plans.
 (3) only keyword `continuation_token` to restart a poller from a saved state.
-  `list_all_orders` renamed to `list_all_reservations`.

### Added

- Added `MicrosoftTeamsUserIdentifier`

##### `IdentityClient`
- Added support for Azure Active Directory authentication

#### `PhoneNumberAdministrationClient`
- Added support for Azure Active Directory authentication
## 1.0.0b3 (2020-11-16)

### Breaking Changes

##### `PhoneNumberSearch` renamed to `PhoneNumberReservation`.

##### `PhoneNumberReservation`
- `search_id` has been renamed to `reservation_id`.

##### `PhoneNumberAdministrationClient`
- `get_search_by_id` has been renamed to `get_reservation_by_id`.
- `create_search` has been renamed to `begin_reserve_phone_numbers`.
-  `begin_reserve_phone_numbers` now takes either `options`, or `continuation_token` keywords as input.
-  `begin_reserve_phone_numbers` now returns `LROPoller[PhoneNumberReservation]`.
- `release_phone_numbers` has been renamed to `begin_release_phone_numbers`.
-  `begin_release_phone_numbers` now takes either `phone_numbers`, or `continuation_token` keywords as input.
-  `begin_release_phone_numbers` now returns `LROPoller[PhoneNumberRelease]`.
- `purchase_search` has been renamed to `begin_purchase_reservation`.
-  `begin_purchase_reservation` now takes either `reservation_id`, or `continuation_token` keywords as input.
-  `begin_purchase_reservation` now returns `LROPoller[PurchaseReservationPolling]`.
- `cancel_search` has been renamed to `cancel_reservation`.

### Added

##### `PhoneNumberAdministrationClient`
- Add long run operation polling method `ReservePhoneNumberPolling`,`PurchaseReservationPolling`,
`ReleasePhoneNumberPolling`.

## 1.0.0b2 (2020-10-06)
- Added support for phone number administration.

## 1.0.0b1 (2020-09-22)
- Preview release of the package.
