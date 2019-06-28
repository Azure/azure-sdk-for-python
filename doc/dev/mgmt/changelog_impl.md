# Automatic ChangeLog

This article describes the automatic changelog system used to generated entries in the ChangeLog of every packages in this repository. Although the current implementation is specific to Autorest generated packages, the logic inside is not, and could be adapted to other type of SDK or other packages.

## Overview

In order to compute this ChangeLog, we do the following steps:
- Build a JSON representation of a package. We describe the more precisely possible every methods, parameters, classes, etc. in a JSON format. We do this step for both the current candidate package and the last one released
- We compute a JSON diff between these two outputs
- We use a "rule" based engine to interpret all entries in the diff in terms of ChangeLog. For example, a node that disappears from the JSONs means a parameters or a methods disappeared.

## Build a JSON report of a package

This is an example of the current JSON format:

```json
{
  "models": {
    "enums": {
      "AvailabilitySetSkuTypes": {
        "name": "AvailabilitySetSkuTypes",
        "type": "Enum",
        "values": [
          "classic",
          "aligned"
        ]
      }
    },
    "exceptions": {},
    "models": {
      "AdditionalCapabilities": {
        "name": "AdditionalCapabilities",
        "type": "Model",
        "parameters": {
          "ultra_ssd_enabled": {
            "name": "ultra_ssd_enabled",
            "properties": {
              "type": "bool",
              "required": false,
              "readonly": false
            }
          }
        }
      }
    }
  },
  "operations": {
    "AvailabilitySetsOperations": {
      "name": "AvailabilitySetsOperations",
      "functions": {
        "create_or_update": {
          "name": "create_or_update",
          "metadata": {
            "url": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/availabilitySets/{availabilitySetName}"
          },
          "parameters": [
            {
              "name": "resource_group_name"
            },
            {
              "name": "availability_set_name"
            },
            {
              "name": "parameters"
            }
          ]
        }
```

The current logic to build this JSON is Python specific right now, we introspect the Python code.

One important concept to allow the best possible diff, is to avoid as much as possible array in the JSON. Arrays are ordered in JSON, so if what you model does not have ordered elements, don't use arrays. For instance, "create_or_update" or "delete" are two operations that are not ordered one to the other, so we don't use an array of operations, but a dictionary where keys are operation name. This has MASSIVE impact on the processing time of the diff.

## Doing the diff

We tried several JSON diff libraries, and currently use JSON-Delta:
https://json-delta.readthedocs.io/en/latest/

This library provides the diff which is the most simple to parse and interpret.

Roughly, this provides an array of tuple:
- Case 1 is the JSON path to apply it on file 1
- Case 2 is the change itself to replace in this JSON path.

Then, if case 2 is empty, this means deletion.

## Creating the ChangeLog

Then we have a set of rules that we apply for each entry in the diff. Currently templated rules are:

```python
## Features
_ADD_OPERATION_GROUP = "Added operation group {}"
_ADD_OPERATION = "Added operation {}.{}"
_MODEL_PARAM_ADD = "Model {} has a new parameter {}"

## Breaking Changes
_REMOVE_OPERATION_GROUP = "Removed operation group {}"
_REMOVE_OPERATION = "Removed operation {}.{}"
_SIGNATURE_CHANGE = "Operation {}.{} has a new signature"
_MODEL_SIGNATURE_CHANGE = "Model {} has a new signature"
_MODEL_PARAM_DELETE = "Model {} no longer has parameter {}"
_MODEL_PARAM_ADD_REQUIRED = "Model {} has a new required parameter {}"
_MODEL_PARAM_CHANGE_REQUIRED = "Parameter {} of model {} is now required"
```

We right now explore the JSON diff in Python, but this could be done with a set of JSON path rules to be more generic if necessary.
