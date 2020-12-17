### Breaking Changes Detector Tool


#### How to opt-in to running the tool in CI

### How to run locally with tox

### How to ignore a reported breaking change


(<breaking-change-type>, <module-name>, <class-name>, <function-name>)
module_name, class_name, function_name should be the name used in the stable/GA version of the library

Examples:

```python
IGNORE_BREAKING_CHANGES = {
    "azure-ai-formrecognizer": [
        ("RemovedOrRenamedClientMethod", "azure.ai.formrecognizer.aio", "FormTrainingClient", "begin_training"),
        ("RemovedOrRenamedModel", "azure.ai.formrecognizer", "FormElement"),
    ],
    "azure-storage-queue": [
        ("RemovedOrRenamedModule", "azure.storage.queue.aio"),
        ("RemovedOrRenamedModuleLevelFunction", "azure.storage.queue", "generate_queue_sas")
    ]
}
```



Types of Breaking Changes Detected by this tool
> Note that this does not cover every kind of breaking change possible

| Breaking Change Type                                 | Explained (changes are relative to the stable library version)                                                         | Ignore signature IF an approved breaking change or false positive                  |
|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| RemovedOrRenamedModule                               | An entire module was removed or renamed in the current version. E.g. `aio` module was removed.                         | ("RemovedOrRenamedModule", "module-name")
| RemovedOrRenamedClient                               | A client was removed or renamed in the current version.                                                                | ("RemovedOrRenamedClient", "module-name", "client-name")
| RemovedOrRenamedClientMethod                         | A client method was removed or renamed in the current version.                                                         | ("RemovedOrRenamedClientMethod", "module-name", "client-name", "function-name")                                             
| RemovedOrRenamedModel                                | A model or publicly exposed class was removed or renamed in the current version.                                       | ("RemovedOrRenamedModel", "module-name", "class-name")                                                                                                      
| RemovedOrRenamedModelMethod                          | A model or publicly exposed class' method was removed or renamed in the current version.                               | ("RemovedOrRenamedModelMethod", "module-name", "class-name", "function-name")                                                                                          
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
                                       
