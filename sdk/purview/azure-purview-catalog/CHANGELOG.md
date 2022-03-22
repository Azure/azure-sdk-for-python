# Release History

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
