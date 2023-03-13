# Propagating additional information to tracing spans

Associated PR: https://github.com/Azure/azure-sdk-for-python/pull/29327

## Problem

Information needed in `distributed_trace` decorator:

- SDK package name
- SDK package version
- SDK resource provider name

This info is then passed to created span.

## Solution

Store these values as constants in some location where they can be accessed by the decorators.

### Where to store resource provider constants?

In base namespace. Options:

`azure/storage/blob/`

1. In `_version.py` as constants like `VERSION` already is:
    ```python
    VERSION = "12.16.0b1"
    RESOURCE_PROVIDER = "Microsoft.Storage"
    PACKAGE_NAME = "azure-storage-blob"
    ```
2. Or, in `__init__.py` as dunder variables:
    ```python
    __version__ = VERSION
    __resource_provider__ = "Microsoft.Storage"
    __package_name__ = "azure-storage-blob"
    ```

### How should `distributed_trace` decorators obtain these values?

- **Option 1: Pass them in as arguments to the decorator**
    - Pros: Simple to implement with no discernible perf overhead.
    - Cons: Need to pass them in everywhere and repeatedly for each SDK method that uses the decorator.

    ```python
    @distributed_trace(resource_provider=resource_provider, package_name=package_name, package_version=package_version)
    ```

- **Option 2: Use `getattr` to get the values from the module**
    - Pros:
        - No need to pass arguments from decorator, so much less changes on SDK side.
        - Even if SDK hasn't been update with values, the logic can still deduce at least the base module name and version which
          can be used in the tracer instrumentation scope.
    - Cons:
        - Additional perf overhead on the core side. However, this is fairly
        and only applicable when tracing is enabled. Repeated calls
          are very fast with the lru_cache being used.

    - Example implementations:

        1. `_version` search implementation:

            ```python
            @lru_cache(maxsize=128)
            def _get_module_info(func: Callable) -> Tuple[Optional[str], Optional[str], Optional[str]]:
                module_parts = func.__module__.split(".")
                # Traverse backwards through module name until we find a _version module.
                for i in range(len(module_parts), 0, -1):
                    try:
                        module_name = ".".join(module_parts[:i])
                        version_module = f"{module_name}._version"
                        if version_module in sys.modules:
                            module = sys.modules[version_module]

                            version = getattr(module, "VERSION", None)
                            package_name = getattr(module, "PACKAGE_NAME", module_name)
                            resource_provider = getattr(module, "RESOURCE_PROVIDER", None)

                            return package_name, version, resource_provider
                    except Exception:  # pylint: disable=broad-except
                        pass
                return None, None, None
            ```
            This looks for `_version.py` in the module hierarchy, and if it finds it, it will use the values from there.

            Sample input: func with module name = `azure.storage.blob._generated.operations._service_operations`

            The function above would eventually find `azure.storage.blob._version` and will return the values from there.

            This function adds, on average, 5-7% overhead to the decorator (about .000011 seconds on my system).

        2. `__version__` search implementation:

            ```python
            @lru_cache(maxsize=128)
            def _get_module_info_alt(func: Callable) -> Tuple[Optional[str], Optional[str], Optional[str]]:
                print(func.__module__)
                module_parts = func.__module__.split(".")
                # Traverse backwards through module name until we find a _version module.
                for i in range(len(module_parts), 0, -1):
                    try:
                        module_name = ".".join(module_parts[:i])
                        module = sys.modules[module_name]
                        if hasattr(module, "__version__"):
                            version = module.__version__
                            package_name = getattr(module, "__package_name__", module_name)
                            resource_provider = getattr(module, "__resource_provider__", None)

                            return package_name, version, resource_provider
                    except Exception:  # pylint: disable=broad-except
                        pass
                return None, None, None
            ```

            Sample input: func with module name = `azure.storage.blob._generated.operations._service_operations`

            The function above would eventually find `azure.storage.blob.__version__` and will make the assumption that the other dunder variables can be found where `__version__` was found.

            This adds about a 15-20% overhead to the decorator (about .000035 seconds on my system)

            When a decoratred operation call generally takes in the order of tenths of seconds (e.g., ~.15 seconds), both additional overheads are insignificant.
