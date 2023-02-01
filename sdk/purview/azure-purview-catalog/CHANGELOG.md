# Release History

## 1.0.0b5 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b4 (2022-06-13)

**Features**

  - Support Atlas 2.2 APIs

**Bugs Fixed**

  - Add missing query parameter `includeTermHierarchy` for update term API
  - Add missing query parameter `excludeRelationshipTypes` for get term API

## 1.0.0b3 (2022-03-15)

**Bugs Fixed**

  - Fix `delete_by_guids` to get rid of bad request error #22487

## 1.0.0b2 (2021-09-29)

**Features**

  - Add convenience operations to client

**Breaking changes**

  - Remove rest layer and request builders(detailed description is in `README.md`)
  - The HttpRequest parameter to send_request has changed from `http_request` to `request`
  - Ordering of endpoint and credential params have changed


## 1.0.0b1 (2021-05-11)

- This is the initial release of the Azure Purview Catalog library.
