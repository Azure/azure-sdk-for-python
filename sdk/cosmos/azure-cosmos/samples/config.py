import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', '[YOUR ENDPOINT]'),
    'master_key': os.environ.get('ACCOUNT_KEY', '[YOUR KEY]'),
    'database_id': os.environ.get('COSMOS_DATABASE', '[YOUR DATABASE]'),
    'container_id': os.environ.get('COSMOS_CONTAINER', '[YOUR CONTAINER]'),
    'tenant_id': os.environ.get('TENANT_ID', '[YOUR CONTAINER]'),
    'client_id': os.environ.get('COSMOS_CONTAINER', '[YOUR CONTAINER]'),
    'client_secret': os.environ.get('COSMOS_CONTAINER', '[YOUR CONTAINER]'),
}
