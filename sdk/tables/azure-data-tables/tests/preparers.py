import functools
import inspect
import time

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import HttpResponseError
from devtools_testutils import PowerShellPreparer, is_live

CosmosPreparer = functools.partial(
    PowerShellPreparer,
    "tables",
    tables_cosmos_account_name="fakecosmosaccount",
    tables_primary_cosmos_account_key="fakecosmosaccountkey",
)

TablesPreparer = functools.partial(
    PowerShellPreparer,
    "tables",
    tables_storage_account_name="faketableaccount",
    tables_primary_storage_account_key="faketablesaccountkey",
)


def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, "__is_preparer", False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn)  # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]


def tables_decorator(func, **kwargs):
    @TablesPreparer()
    def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_storage_account_key")
        name = kwargs.pop("tables_storage_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_storage_account_key"] = key
        kwargs["tables_storage_account_name"] = name

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

    return wrapper


def cosmos_decorator(func, **kwargs):
    @CosmosPreparer()
    def wrapper(*args, **kwargs):
        key = kwargs.pop("tables_primary_cosmos_account_key")
        name = kwargs.pop("tables_cosmos_account_name")
        key = AzureNamedKeyCredential(key=key, name=name)

        kwargs["tables_primary_cosmos_account_key"] = key
        kwargs["tables_cosmos_account_name"] = name

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        EXPONENTIAL_BACKOFF = 1
        RETRY_COUNT = 0

        try:
            return func(*args, **trimmed_kwargs)
        except HttpResponseError as exc:
            if exc.status_code != 429:
                raise
            print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
            while RETRY_COUNT < 6:
                if is_live():
                    time.sleep(EXPONENTIAL_BACKOFF)
                try:
                    return func(*args, **trimmed_kwargs)
                except HttpResponseError as exc:
                    print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
                    EXPONENTIAL_BACKOFF **= 2
                    RETRY_COUNT += 1
                    if exc.status_code != 429 or RETRY_COUNT >= 6:
                        raise

    return wrapper
