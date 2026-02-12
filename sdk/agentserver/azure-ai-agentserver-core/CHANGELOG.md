# Release History


## 1.0.0b12 (2026-02-12)

### Bugs Fixed

- Minor bugs fixed for -langgraph and -agentframework.


## 1.0.0b11 (2026-02-10)

### Features Added

- Added conversation persistence: automatically save input and output items to conversation when `store=True` in request
- Added deduplication check to avoid saving duplicate input items
- Added server startup success log message

### Other Changes

- Improved logging: replaced confusing print statements with proper logger calls
- Changed logger to use stdout instead of stderr for consistency with uvicorn
- Added `_items_are_equal()` method for comparing conversation items

## 1.0.0b10 (2026-01-27)

### Bugs Fixed

- Make AZURE_AI_PROJECTS_ENDPOINT optional.

## 1.0.0b9 (2026-01-23)

### Features Added

- Integrated with Foundry Tools


## 1.0.0b8 (2026-01-21)

### Features Added

- Support keep alive for long-running streaming responses.


## 1.0.0b7 (2025-12-05)

### Features Added

- Update response with created_by

### Bugs Fixed

- Fixed error response handling in stream and non-stream modes

## 1.0.0b6 (2025-11-26)

### Features Added

- Support Agent-framework greater than 251112


## 1.0.0b5 (2025-11-16)

### Features Added

- Support Tools Oauth

### Bugs Fixed

- Fixed streaming generation issues.


## 1.0.0b4 (2025-11-13)

### Features Added

- Adapters support tools

### Bugs Fixed

- Pin azure-ai-projects and azure-ai-agents version to avoid version confliction


## 1.0.0b3 (2025-11-11)

### Bugs Fixed

- Fixed Id generator format.

- Fixed trace initialization for agent-framework.


## 1.0.0b2 (2025-11-10)

### Bugs Fixed

- Fixed Id generator format.

- Improved stream mode error messsage.

- Updated application insights related configuration environment variables.


## 1.0.0b1 (2025-11-07)

### Features Added

First version
