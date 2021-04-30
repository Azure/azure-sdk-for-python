import functools
import inspect

from azure.core.credentials import AzureNamedKeyCredential
from devtools_testutils import PowerShellPreparer

CosmosPreparer = functools.partial(
    PowerShellPreparer, "tables",
    tables_cosmos_account_name="fake_cosmos_account",
    tables_primary_cosmos_account_key="fakecosmosaccountkey"
)

TablesPreparer = functools.partial(
    PowerShellPreparer, "tables",
    tables_storage_account_name="fake_table_account",
    tables_primary_storage_account_key="faketablesaccountkey"
)


def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, '__is_preparer', False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn) # pylint: disable=deprecated-method
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

        trimmed_kwargs = {k:v for k, v in kwargs.items()}
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

        trimmed_kwargs = {k:v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

    return wrapper

