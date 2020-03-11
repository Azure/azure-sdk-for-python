import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', '[YOUR ENDPOINT]'),
    'master_key': os.environ.get('ACCOUNT_KEY', '[YOUR KEY]'),
    'database_id': os.environ.get('COSMOS_DATABASE', '[YOUR DATABASE]'),
    'container_id': os.environ.get('COSMOS_CONTAINER', '[YOUR CONTAINER]'),
}
