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
        ("RemoveOrRenameClientMethod", "azure.ai.formrecognizer.aio", "FormTrainingClient", "begin_training"),
        ("RemoveOrRenameModel", "azure.ai.formrecognizer", "FormElement"),
    ],
    "azure-storage-queue": [
        ("RemoveOrRenameModule", "azure.storage.queue.aio"),
        ("RemoveOrRenameModuleLevelFunction", "azure.storage.queue", "generate_queue_sas")
    ]
}
```



Types of Breaking Changes Detected by this tool
> Note that this does not cover every kind of breaking change possible

| Breaking Change Type                               | Explained                                                                                                              | Ignore signature IF an approved breaking change or false positive                  |
|----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| RemoveOrRenameClient                               | A client from the stable library was removed or renamed in the current version.                                        | ("RemoveOrRenameClient", "module-name", "client-name")
| RemoveOrRenameClientMethod                         | A client method from the stable library was removed or renamed in the current version.                                 | ("RemoveOrRenameClientMethod", "module-name", "client-name" | "function-name")                                             
| RemoveOrRenameModel                                | A model or publicly exposed class from the stable library was removed or renamed in the current version.               | ("RemoveOrRenameModel", "module-name", "class-name")                                                                                                      
| RemoveOrRenameModelMethod                          | A model or publicly exposed class' method from the stable library was removed or renamed in the current version.       | ("RemoveOrRenameModelMethod", "module-name", "class-name" | "function-name")                                                                                          
| RemoveOrRenameModuleLevelFunction                  | A module level function from the stable library was removed or renamed in the current version.                         | ("RemoveOrRenameModuleLevelFunction", "module-name", "function-name")                                          
| RemoveOrRenamePositionalParam                      | A positional parameter on a function was removed or renamed.                                                           | ("RemoveOrRenamePositionalParam", "module-name", "class-name" | "function-name")                                                    
| AddedPositionalParam                               | `def my_function(param1)  -->  def my_function(param1, param2)`                                                        | ("AddedPositionalParam", "module-name", "class-name" | "function-name") 
| RemovedParameterDefaultValue                       | `def my_function(param=None)  -->  def my_function(param)`                                                             | ("RemovedParameterDefaultValue", "module-name", "class-name" | "function-name")                   
| RemoveOrRenameInstanceAttribute                    | An instance attribute on the class was removed or renamed.                                                             | ("RemoveOrRenameInstanceAttribute", "module-name", "class-name")                                                           
| RemoveOrRenameEnumValue                            | An enum value was removed or renamed.                                                                                  | ("RemoveOrRenameEnumValue", "module-name", "class-name")                                 
| ChangedParameterDefaultValue                       | `def my_function(param="delete")  -->  def my_function(param="delete_if_exists")`                                      | ("ChangedParameterDefaultValue", "module-name", "class-name" | "function-name")                                                                              
| ChangedParameterOrdering                           | `def my_function(a, b, c=None)  -->  def my_function(b, c=None, a=None)`                                               | ("ChangedParameterOrdering", "module-name", "class-name" | "function-name") 
| ChangedParameterType                               | `def my_function(a, b, c)  -->  def my_function(a, b, *, c)`                                                           | ("ChangedParameterType", "module-name", "class-name" | "function-name")               
| ChangedFunctionType                                | `async def my_function(param) ->  def my_function(param)`                                                              | ("ChangedFunctionType", "module-name", "class-name" | "function-name")                                       
| RemoveOrRenameModule                               | An entire module was removed or renamed in the current version.                                                        | ("RemoveOrRenameModule", "module-name")                                                      
| RemovedFunctionKwargs                              | A function was changed to no longer accept keyword arguments. `def my_func(param, **kwargs)  -->  def my_func(param)`  | ("RemovedFunctionKwargs", "module-name", "class-name" | "function-name")  