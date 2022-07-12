# Release History

## 1.2.0 (2022-05-31)
 - GA release

## 1.2.0b1 (2022-03-31)

### Bugs Fixed

- Update `azure-core` dependency to avoid inconsistent dependencies from being installed.

### Other Changes

- Python 2.7 and 3.6 are no longer supported. Please use Python version 3.7 or later.


## 1.1.0 (2020-11-24)

- The is the GA release containing the following changes:

**API updates**
- Added etag and match_condition parameters to upsert_digital_twin and upsert_relationship APIs to support conditional operation.
- Renamed `EventRoute` model to `DigitalTwinsEventRoute`.
- Removed unsed `azure.digitaltwins.core.QueryResult` object.
- Renamed the `component_path` to `component_name`
- Renamed the `payload` parameter to `telemetry` and made `message_id` a keyword-only parameter.

**Bug Fixes**
- The `relationship` parameter in `DigitalTwinsClient.upsert_relationship` is required and has been amended accordingly.
- The `json_patch` parameter in `DigitalTwinsClient.update_relationship` is required and has been amended accordingly.
- Renamed `models` parameter to `dtdl_models` in `DigitalTwinsClient.create_models`. This is now required.
- The `dependencies_for` parameter in `DigitalTwinsClient.list_models` is optional and has been amended accordingly.
- Match condition parameters have been fixed. Where invalid match conditions are supplied, a `ValueError` will be raised.
- Fixed double await on async listing operations.

**Documentation**
- User Agent value updated according to guidelines.
- Updated JSON patch parameter typehints to `List[Dict[str, object]]`.
- Updated constructor credential typehint to `azure.core.credentials.TokenCredential`
- Samples and documentation updated. 


## 1.0.0b1 (2020-10-31)

* Initial Release
