# Azure Maps Search for Python

> see https://aka.ms/autorest

## Setup

```ps

npm install -g autorest
```

## Generation

```ps

cd <swagger-folder>
autorest SWAGGER.md
```

To generate this file, simply type

```ps

autorest swagger/README.md --python-sdks-folder=<location-of-your-sdk-dir>
```

We automatically hardcode in that this is `python`.

## Basic Information

```yaml
tag: package-2023-06
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Search/readme.md
output-folder: ../azure/maps/search/_generated
namespace: azure.maps.search
package-name: azure-maps-search
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: MapsSearchClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
directive:
  # Rename BoundaryResultTypeEnum
  - from: swagger-document
    where: "$.parameters.BoundaryResultType.x-ms-enum"
    transform: >
      $["name"] = "BoundaryResultType";

  # Rename ResolutionEnum
  - from: swagger-document
    where: "$.parameters.Resolution.x-ms-enum"
    transform: >
      $["name"] = "Resolution";

  # Rename UsageTypeEnum
  - from: swagger-document
    where: "$.definitions.UsageType.x-ms-enum"
    transform: >
      $["name"] = "UsageType";

  # Rename MatchCodesEnum
  - from: swagger-document
    where: "$.definitions.MatchCodes.items.x-ms-enum"
    transform: >
      $["name"] = "MatchCodes";

  # Rename ConfidenceEnum
  - from: swagger-document
    where: "$.definitions.Confidence.x-ms-enum"
    transform: >
      $["name"] = "Confidence";

  # Rename FeatureTypeEnum
  - from: swagger-document
    where: "$.definitions.FeaturesItem.properties.type.x-ms-enum"
    transform: >
      $["name"] = "FeatureType";

  # Rename FeatureCollectionEnum
  - from: swagger-document
    where: "$.definitions.FeatureCollectionType.x-ms-enum"
    transform: >
      $["name"] = "FeatureCollection";

  # Rename CalculationMethodEnum
  - from: swagger-document
    where: "$.definitions.GeocodePoints.items.properties.calculationMethod.x-ms-enum"
    transform: >
      $["name"] = "CalculationMethod";

  # Rename ResultTypeEnum
  - from: swagger-document
    where: "$.parameters.ReverseGeocodingResultTypes.items.x-ms-enum"
    transform: >
      $["name"] = "ResultType";

  # Rename ReverseGeocodingResultTypeEnum
  - from: swagger-document
    where: "$.definitions.ReverseGeocodingBatchRequestItem.properties.resultTypes.items.x-ms-enum"
    transform: >
      $["name"] = "ReverseGeocodingResultType";
```
