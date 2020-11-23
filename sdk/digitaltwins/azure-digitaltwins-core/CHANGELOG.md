# Release History

## 1.1.0 (2020-11-24)

**Bug Fixes**
- The `relationship` parameter in `DigitalTwinsClient.upsert_relationship` is required and has been amended accordingly.
- The `json_patch` parameter in `DigitalTwinsClient.update_relationship` is required and has been amended accordingly.
- The `dtdl_models` parameter in `DigitalTwinsClient.create_models` is required and has been amended accordingly.
- The `dependencies_for` parameter in `DigitalTwinsClient.list_models` is optional and has been amended accordingly.
- Match condition parameters have been fixed. Where invalid match conditions are supplied, a `ValueError` will be raised.
- Removed unsed `azure.digitaltwins.core.QueryResult` object.
- Fixed double await on async listing operations.

**Documentation**
- User Agent value updated according to guidelines.
- Updated JSON patch parameter typehints to `List[Dict[str, object]]`.
- Updated constructor credential typehint to `azure.core.credentials.TokenCredential`
- Samples and documentation updated. 


## 1.0.0 (unreleased)

- The is the GA release containing the following changes:
  - Added etag and match_condition parameters to upsert_digital_twin and upsert_relationship APIs to support conditional operation.
  - Rename EventRoute type to DigitalTwinsEventRoute
  - Rename component_path to component_name
  - Rename models to dtdl_models
  - Fix some documentation

## 1.0.0b1 (2020-10-31)

* Initial Release
