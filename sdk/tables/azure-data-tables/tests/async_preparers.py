import time

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import HttpResponseError

from devtools_testutils import is_live

from preparers import CosmosPreparer, TablesPreparer, trim_kwargs_from_test_function


def cosmos_decorator_async(func, **kwargs):
    @CosmosPreparer()
    async def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_cosmos_account_key")
        name = kwargs.pop("tables_cosmos_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_cosmos_account_key"] = key
        kwargs["tables_cosmos_account_name"] = name

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        return await func(*args, **trimmed_kwargs)

    return wrapper


def tables_decorator_async(func, **kwargs):
    @TablesPreparer()
    async def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_storage_account_key")
        name = kwargs.pop("tables_storage_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_storage_account_key"] = key
        kwargs["tables_storage_account_name"] = name

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        EXPONENTIAL_BACKOFF = 1.5
        RETRY_COUNT = 0

        try:
            return await func(*args, **trimmed_kwargs)
        except HttpResponseError as exc:
            if exc.status_code != 429:
                raise
            print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
            while RETRY_COUNT < 6:
                if is_live():
                    time.sleep(EXPONENTIAL_BACKOFF)
                try:
                    return await func(*args, **trimmed_kwargs)
                except HttpResponseError as exc:
                    print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
                    EXPONENTIAL_BACKOFF **= 2
                    RETRY_COUNT += 1
                    if exc.status_code != 429 or RETRY_COUNT >= 6:
                        raise

    return wrapper
