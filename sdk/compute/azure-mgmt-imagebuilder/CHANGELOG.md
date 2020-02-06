# Release History

## 0.3.0 (2019-11-19)

**Features**

  - Model ImageTemplatePowerShellCustomizer has a new parameter
    run_elevated
  - Model ImageTemplatePowerShellCustomizer has a new parameter
    sha256_checksum
  - Model ImageTemplate has a new parameter vm_profile
  - Model ImageTemplateFileCustomizer has a new parameter
    sha256_checksum
  - Model ImageTemplateShellCustomizer has a new parameter
    sha256_checksum

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ImageBuilderClient cannot be imported from
    `azure.mgmt.imagebuilder.image_builder_client` anymore (import
    from `azure.mgmt.imagebuilder` works like before)
  - ImageBuilderClientConfiguration import has been moved from
    `azure.mgmt.imagebuilder.image_builder_client` to
    `azure.mgmt.imagebuilder`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.imagebuilder.models.my_class` (import
    from `azure.mgmt.imagebuilder.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.imagebuilder.operations.my_class_operations` (import
    from `azure.mgmt.imagebuilder.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.1 (2019-04-25)

**Bugfixes**

  - Add missing build_timeout_in_minutes
  - Fix some regexp checking

## 0.2.0 (2019-04-12)

  - New API version 2019-05-01-preview

## 0.1.0 (2019-04-09)

  - Initial Release
