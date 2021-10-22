from azure.core.exceptions import AzureError

class SchemaParseError(AzureError):
    def __init__(self, message, *args, **kwargs):
        super(SchemaParseError, self).__init__(message, *args, **kwargs)

class SchemaSerializationError(AzureError):
    def __init__(self, message, *args, **kwargs):
        super(SchemaSerializationError, self).__init__(message, *args, **kwargs)

class SchemaDeserializationError(AzureError):
    def __init__(self, message, *args, **kwargs):
        super(SchemaDeserializationError, self).__init__(message, *args, **kwargs)
