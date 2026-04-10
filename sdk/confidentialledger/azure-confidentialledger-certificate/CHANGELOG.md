# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- Added redirect URL caching for write operations (POST/PUT/PATCH/DELETE). After the first redirect from the load balancer, subsequent writes go directly to the primary node, significantly reducing latency.
- Added `disable_redirect_cleanup=True` to preserve authentication headers during redirects.

## 1.0.0b1 (2025-10-13)

### Other Changes

- Initial version
