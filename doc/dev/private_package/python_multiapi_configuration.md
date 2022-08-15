This doc describes how to configure multi-api package for Python.

# Multi-Api Package

When `readme.python.md` has `Python multi-api`, the package is multi-api package.

# Configuration

When you want to release a new version for multi-api package, check the following steps:

## 1.target tag

Make sure the target tag is defined in `readme.md`. For example, you want to release new tag `package-2021-05-01` for `azure-mgmt-network`, it should be defined in [readme.md](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/network/resource-manager#tag-package-2021-05).

the target tag should only contain files from one folder:

![](one_folder.png)

If your tag contains files from different folders, you need to define some split tags. For example: `ApplicationInsights` has [Tag: package-2021-11-01](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/applicationinsights/resource-manager#tag-package-2021-11-01), but it contains different folders. If you want to publish the package for the tag, you need to split it to different tags: [sample](https://github.com/Azure/azure-rest-api-specs/pull/16799/files)

![](different_folders.png)

![](split_tag.png)



## 2.Configure `readme.python.md`

Let us set `azure-mgmt-network` as example, if you want to release `package-2021-03-01`, you need to add the following definition in `readme.python.md`:

[Update readme.python.md by BigCat20196 · Pull Request #15818 · Azure/azure-rest-api-specs (github.com)](https://github.com/Azure/azure-rest-api-specs/pull/15818/files)

![](python_config.png)