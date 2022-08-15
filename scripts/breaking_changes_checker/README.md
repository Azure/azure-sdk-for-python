# Breaking Changes Detector Tool

The breaking changes tool compares the last stable/GA version of the library (if it exists) against the current code
(in main) and reports any breaking changes found.

## How to opt-in to running the tool in CI

Add your package name to the `RUN_BREAKING_CHANGES_PACKAGES` found [here](https://github.com/Azure/azure-sdk-for-python/tree/main/scripts/breaking_changes_checker/breaking_changes_allowlist.py).

## Run locally with tox

**1) Install tox and tox-monorepo:**

`pip install tox tox-monorepo`

**2) Run the `breaking` environment.**

Here we run the breaking changes tool against azure-storage-blob, for example:

`C:\azure-sdk-for-python\sdk\storage\azure-storage-blob>tox -c ../../../eng/tox/tox.ini -e breaking`


## Ignore a reported breaking change

A breaking change reported by this tool may be an acceptable change. If it is an **approved** breaking change (signed off by architecture board)
or a false positive, then you should add the breaking change to the ignore list.

The ignore list is found [here](https://github.com/Azure/azure-sdk-for-python/tree/main/scripts/breaking_changes_checker/breaking_changes_allowlist.py).

To add an ignore, you will need the identifier of the breaking change. This includes the breaking change type,
module name, and optionally class and/or function name, in this order, e.g.

`(breaking-change-type, module-name, class-name, function-name)`

Add this signature as a list of tuples under your package name in the [IGNORE_BREAKING_CHANGES](https://github.com/Azure/azure-sdk-for-python/tree/main/scripts/breaking_changes_checker/breaking_changes_allowlist.py) dictionary.
Note that the names used should be those from the _stable_ package. If I renamed my function from `begin_training` to
`begin_train_model`, I would put `begin_training` as my function name.

See ignore signature skeletons for each type of breaking change [below](#types-of-breaking-changes-detected)

**Examples:**

```python
IGNORE_BREAKING_CHANGES = {
    "azure-ai-formrecognizer": [
        ("RemovedOrRenamedClientMethod", "azure.ai.formrecognizer.aio", "FormTrainingClient", "begin_training"),
        ("RemovedOrRenamedClass", "azure.ai.formrecognizer", "FormElement"),
    ],
    "azure-storage-queue": [
        ("RemovedOrRenamedModule", "azure.storage.queue.aio"),
        ("RemovedOrRenamedModuleLevelFunction", "azure.storage.queue", "generate_queue_sas")
    ]
}
```


## Types of Breaking Changes Detected

> Note that this does not cover every kind of breaking change possible.

| Breaking Change Type                                 | Explained (changes are relative to the stable/GA library version)                                                      | Ignore signature IF an approved breaking change or false positive                  |
|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| RemovedOrRenamedModule                               | An entire module was removed or renamed in the current version. E.g. `aio` module was removed.                         | ("RemovedOrRenamedModule", "module-name")
| RemovedOrRenamedClient                               | A client was removed or renamed in the current version.                                                                | ("RemovedOrRenamedClient", "module-name", "client-name")
| RemovedOrRenamedClientMethod                         | A client method was removed or renamed in the current version.                                                         | ("RemovedOrRenamedClientMethod", "module-name", "client-name", "function-name")
| RemovedOrRenamedClass                                | A model or publicly exposed class was removed or renamed in the current version.                                       | ("RemovedOrRenamedClass", "module-name", "class-name")
| RemovedOrRenamedClassMethod                          | A model or publicly exposed class' method was removed or renamed in the current version.                               | ("RemovedOrRenamedClassMethod", "module-name", "class-name", "function-name")
| RemovedOrRenamedInstanceAttribute                    | An instance attribute was removed or renamed in the current version.                                                   | ("RemovedOrRenamedInstanceAttribute", "module-name", "class-name")
| RemovedOrRenamedEnumValue                            | An enum value was removed or renamed in the current version                                                            | ("RemovedOrRenamedEnumValue", "module-name", "class-name")
| RemovedOrRenamedModuleLevelFunction                  | A module level function was removed or renamed in the current version.                                                 | ("RemovedOrRenamedModuleLevelFunction", "module-name", "function-name")
| RemovedOrRenamedPositionalParam                      | A positional parameter on a function was removed or renamed.                                                           | ("RemovedOrRenamedPositionalParam", "module-name", "class-name", "function-name")
| AddedPositionalParam                                 | `def my_function(param1)  -->  def my_function(param1, param2)`                                                        | ("AddedPositionalParam", "module-name", "class-name", "function-name")
| RemovedParameterDefaultValue                         | `def my_function(param=None)  -->  def my_function(param)`                                                             | ("RemovedParameterDefaultValue", "module-name", "class-name", "function-name")
| ChangedParameterDefaultValue                         | `def my_function(param="yellow")  -->  def my_function(param="blue")`                                                  | ("ChangedParameterDefaultValue", "module-name", "class-name", "function-name")
| ChangedParameterOrdering                             | `def my_function(a, b, c=None)  -->  def my_function(b, c=None, a=None)`                                               | ("ChangedParameterOrdering", "module-name", "class-name", "function-name")
| RemovedFunctionKwargs                                | A function was changed to no longer accept keyword arguments. `def my_func(param, **kwargs)  -->  def my_func(param)`  | ("RemovedFunctionKwargs", "module-name", "class-name", "function-name")
| ChangedParameterKind                                 | `def my_function(a, b, c)  -->  def my_function(a, b, *, c)`                                                           | ("ChangedParameterKind", "module-name", "class-name", "function-name")
| ChangedFunctionKind                                  | `async def my_function(param) ->  def my_function(param)`                                                              | ("ChangedFunctionKind", "module-name", "class-name", "function-name")

