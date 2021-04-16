# Release History

## 1.0.0b5 (Unreleased)


## 1.0.0b4 (2021-04-13)
### Breaking Changes
- This package has been deprecated. Please use [azure-communication-identity](https://pypi.org/project/azure-communication-identity/) and [azure-communication-phonenumbers](https://pypi.org/project/azure-communication-phonenumbers/) instead.

## 1.0.0b3 (2020-11-16)

**Breaking Changes**

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

**New Features**

##### `PhoneNumberAdministrationClient`
- Add long run operation polling method `ReservePhoneNumberPolling`,`PurchaseReservationPolling`,
`ReleasePhoneNumberPolling`.

## 1.0.0b2 (2020-10-06)
- Added support for phone number administration.

## 1.0.0b1 (2020-09-22)
- Preview release of the package.
