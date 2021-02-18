import functools
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