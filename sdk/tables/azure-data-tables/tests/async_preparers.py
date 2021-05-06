import functools

from azure.core.credentials import AzureNamedKeyCredential
from preparers import CosmosPreparer, TablesPreparer, trim_kwargs_from_test_function

def cosmos_decorator_async(func, **kwargs):

    @CosmosPreparer()
    def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_cosmos_account_key")
        name = kwargs.pop("tables_cosmos_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_cosmos_account_key"] = key
        kwargs["tables_cosmos_account_name"] = name

        trimmed_kwargs = {k:v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            return await func(*args, **trimmed_kwargs)
        return wrapped

    return wrapper


def tables_decorator_async(func, **kwargs):

    @TablesPreparer()
    def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_storage_account_key")
        name = kwargs.pop("tables_storage_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_storage_account_key"] = key
        kwargs["tables_storage_account_name"] = name

        trimmed_kwargs = {k:v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            return await func(*args, **trimmed_kwargs)
        return wrapped

    return wrapper
