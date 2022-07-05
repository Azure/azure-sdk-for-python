# Release History

## 0.1.0b6 (2022-07-06)

### Features Added

- Allow Input/Output objects to be used by CommandComponent.
- Added MoonCake cloud support.
- Unified inputs/outputs building and validation logic in BaseNode.
- Allow Git repo URLs to be used as code for jobs and components.
- Updated AutoML YAML schema to use InputSchema.
- Added end_time to job schedule.
- MIR and pipeline job now support registry assets.

### Breaking Changes

### Bugs Fixed

- Have mldesigner use argparser to parse incoming args.
- Bumped pyjwt version to <3.0.0.
- Reverted "upload support for symlinks".
- Error message improvement when a YAML UnionField fails to match.
- Reintroduced support for symlinks when uploading.
- Hard coded registry base URL to eastus region to support preview.

## 0.1.0b4 (unreleased)

## 0.1.0b3 (2022-05-24)

### Features Added

- First preview.
