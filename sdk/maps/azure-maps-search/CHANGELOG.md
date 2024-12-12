# Release History

## 2.0.0b3 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 2.0.0b2 (2024-12-12)

### Features Added

- Integrated support for SAS-based authentication

## 2.0.0b1 (2024-08-06)

### New Features and Enhancements

- Support Search API `2023-06-01`

- **Geocoding APIs**
  - Introduced `get_geocoding` method to obtain longitude and latitude coordinates for a given address.
  - Introduced `get_geocoding_batch` method to handle batch geocoding queries, supporting up to 100 queries in a single request.

- **Reverse Geocoding APIs**
  - Introduced `get_reverse_geocoding` method to get address details from given coordinates.
  - Introduced `get_reverse_geocoding_batch` method to handle batch reverse geocoding queries, supporting up to 100 queries in a single request.

- **Boundary APIs**
  - Introduced `get_polygon` method to obtain polygon boundaries for a given set of coordinates with specified resolution and boundary result type.

### Breaking Changes

- **Removed Methods**
  - Removed the `fuzzy_search` method.
  - Removed the `search_point_of_interest` method.
  - Removed the `search_address` method.
  - Removed the `search_nearby_point_of_interest` method.
  - Removed the `search_point_of_interest_category` method.
  - Removed the `search_structured_address` method.
  - Removed the `get_geometries` method.
  - Removed the `get_point_of_interest_categories` method.
  - Removed the `reverse_search_address` method.
  - Removed the `reverse_search_cross_street_address` method.
  - Removed the `search_inside_geometry` method.
  - Removed the `search_along_route` method.
  - Removed the `fuzzy_search_batch` method.
  - Removed the `search_address_batch` method.

## 1.0.0b3 (2024-05-15)
 
### Bugs Fixed

- Fix response validation error for reverse search address

### Other Changes

- Fix reverse search sample in README.md
- Fix Sphinx errors
- Fix pylint errors for pylint version 2.15.8

## 1.0.0b2 (2022-10-11)

### Other Changes

- Update the tests using new test proxy
- Update Doc strings

## 1.0.0b1 (2022-09-06)

- Initial Release
