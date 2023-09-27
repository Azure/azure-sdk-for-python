# Multi-api packaging and ARM SDK

Several SDKs on this repository are able to support multi-api in a single package. If you're a SDK maintainer, this documentation explains the rational of it, and the technical details.

## Overview and rationale

### Multi-api, what does it mean?

It means a given specific package is able to do calls to several different API versions of a given service in the same installation and Python process. Example: using `azure-mgmt-compute`, you can get a VM object using API version 2019-03-01, but also 2015-06-15 or 2018-04-01, etc. and not only using the latest API version that exists.

### Why would I need to call anything else than the latest API version?

Because there is different flavors of Azure that are not necessarily provided with the same set of API versions. For example Azure Government, Azure Stack usually needs a few months to get the latest available API version.

### Why a multi-api package?

Indeed, a simple solution would be to write down explicitly what version of SDK supports what API version. Example: 1.0 supports 2015-06-01, 2.0 supports 2017-07-01, etc. The story for customers then would be to pin the specific SDK version for the specific API version they need. However, this was considered unacceptable in an end-to-end scenario:
- It means you cannot install in the same Python environment packages that would target different cloud (Python doesn't allow installation of different versions of the same package together). Azure CLI or Ansible supports for different clouds would then be extremely complicated.
- This forces customers to use old SDK, that might have been fixed on different axis than API version (security fixes, new SDK features like async, etc.)
- Customers rarely needs only one package, but a set of them (storage, compute, network, etc.) and having to keep track of the correct list of packages is challenging.

By providing package that supports multiple API versions we are solving all these issues:
- Simply install "azure-mgmt-compute" and you know it will provide all features for all clouds
- Install the latest one, it will provide all security and features and still contains all necessary API versions for all clouds.
- We can create the notion of "Azure Profile", which is a configuration file that configures automatically all the installed packages to the correct version of a given cloud.

### Is the package too big then, all these API versions?

Autorest for Python v4 has been designed to reduce the size of multi-api packages up to 80% in some scenarios. There is work in progress to do more and scale as necessary for a future version of Autorest.

### Does some API version get deprecated some time and removed from packages?

No, until ARM supports an API version it stays in the package. That could be a massive breaking change otherwise, to force customers to update an API version.

## Technical details

### Details about ARM, resource providers, resource types and Swaggers

ARM is split by resource providers, themself split by resource types. The API version is actually defined at the resource type level (you can get an overview of equivalence between resource types and API version using the CLI: `az provider list`).

To simplify multi-api packaging, it's recommended that each resource type are written in their own file, and that all operations in that file are prefixed by the same operation group.
Example:
Network interfaces operations are defines in a [network interface file](https://github.com/Azure/azure-rest-api-specs/blob/2a65faa9ddbf9970708ba507eeb8071a2d310b57/specification/network/resource-manager/Microsoft.Network/stable/2019-04-01/networkInterface.json), and all operations in this file are prefixed with `NetworkInterfaces_`.

**Python multi-api packaging is based on the assumptions that it's true.** If it's not, it's usually ok but requires a little more subtle packaging (see final section here)

Being that a given Swagger defines only *one* fixed API version, doing multi-api version in one package implies shipping several Swagger files into one package. This is archived by the `batch` directive of Autorest. More details on how to write Readme for Swagger in the specific page for it [swagger_conf.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/swagger_conf.md).

Python SDK team is responsible to design the correct set of tags to set for the `batch` node. Each line of the batch directive should contains only *one* api version to match the folder name used. this might require adding new tags in the readme.md that are specific to only one API version. These tags are usually suffixed by "-only" ([example with compute](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/compute/resource-manager#tag-package-2019-03-01-only))

 In order to simplify this work, there is script called [multi_api_readme_help](https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/multi_api_readme_help.py) that will scan all the Swaggers of a given folder, and suggest:
- a list of tags for the main readme.md
- a batch configuration for the readme.python.md

Note that this script is experimental, and the suggested output might need to be adjusted.

### Azure profile

An azure profile is an official, stamped by Microsoft, mapping between a set of resource types and the correct supported API versions. A profile is the only way right now to characterize a complete of set of ARM resources mapping together. Profiles are checked in in this place: https://github.com/Azure/azure-rest-api-specs/tree/main/profile

### Overview of a multi-api client

Main design guidelines:
- For people on public Azure, API must **NOT** be required parameters:
  e.g. `client = ComputeManagementClient(credentials, sub_id)`
- For people that want a specific API version for a specific need, specifying API version should be possible
  e.g. `client = ComputeManagementClient(credentials, sub_id, api_version='2018-06-01')`
- For people who target a single Azure Profile, specifying it should be be possible
  e.g. `client = ComputeManagementClient(credentials, sub_id, profile=KnownProfile.v2018_06_01_hybrid)`

The first condition has impact on models loading, by default they should load the latest API version transparently:
```python
# Loads the latest version of the model
from azure.mgmt.compute.models import VirtualMachineCreateParameter
```

### Structure of a multi-api package

```
o
`-- azure
    `-- mgmt
        `-- network
            |-- __init__.py
            |-- _configuration.py
            |-- _network_management_client.py
            |-- _operations_mixin.py
            |-- models.py
            |-- version.py
            |-- v2019_04_01
            |   |-- models
            |   |-- operations
            |   |-- __init__.py
            |   |-- _configuration.py
            |   |-- _network_management_client.py
            |   `-- version.py
            `-- v2018_10_01
                |-- models
                |-- operations
                |-- __init__.py
                |-- _configuration.py
                |-- _network_management_client.py
                `-- version.py
```

- There is as many folder per API versions we want to ship
- The files in the API version folders are generated by Autorest
- The files are the root (here `azure/mgmt/network`) are generated by the script [multiapi_init_gen.py](https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/multiapi_init_gen.py)

## Complicated scenarios

### One operation group is defined across several files.

If this is the same API version, since they will be packed together that's ok (for instance [compute](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/compute/resource-manager/Microsoft.Compute/ComputeRP/stable/2019-03-01/compute.json) and [runcommands](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/compute/resource-manager/Microsoft.Compute/ComputeRP/stable/2019-03-01/runCommands.json) shares `VirtualMachines_` but exists always in the same API version)

If this is not the same API version, then we need to bend the rules a little: we need to understand the intent, and decide which API version we use as folder to ship both (example: [ACR 2019-05-01](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/containerregistry/resource-manager/Microsoft.ContainerRegistry/stable/2019-05-01/containerregistry.json) and [registry build 2019-06-01-preview](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/containerregistry/resource-manager/Microsoft.ContainerRegistry/preview/2019-06-01-preview) are shipped as [2019-06-01-preview](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/containerregistry/azure-mgmt-containerregistry/azure/mgmt/containerregistry/v2019_06_01_preview) because they share `BuildRegistry_` operation group).

## Possible improvements

Current implementation assumes operation group are unique, and as discussed it's not always the case. Also, this limitation has impact on intellisense right now. Example, if a user types `compute_client.virtual_machines.` and hit the intellisense shortcut, users won't see any suggestions. It's because the `virtual_machines` property is dynamic and can change depending of dynamic configuration.
