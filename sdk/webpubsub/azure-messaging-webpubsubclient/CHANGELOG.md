# Release History

## 1.1.1 (2024-XX-XX)

### Other Changes

- Clean useless warnings in log

## 1.1.0 (2024-04-24)

### Features Added

- Add Async API with same name of Sync API
- Add api `is_connected`

### Other Changes

- Change default reconnect times to unlimited
- Optimize reconnect/recover logic
- Optimize error message hint when failed to open client
- Optimize typing annotations
- Optimize close logic for Sync API.

## 1.0.0 (2024-01-31)

### Features Added

- Add Operation `open/close`

### Breaking Changes

- Rename operation `on` to `subscribe`
- Rename operation `off` to `unsubscribe`
- Remove model `DisconnectedError`
- Rename model `OpenWebSocketError` to `OpenClientError`
- Remove model `StartClientError`
- Remove model `StartNotStoppedClientError`
- Remove model `DisconnectedError`

### Other Changes

- Add docstring
- First GA

## 1.0.0b1 (2023-04-25)

- Initial version
