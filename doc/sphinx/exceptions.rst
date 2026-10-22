Exception handling
==================

.. important:: This document concerns every package except `azure-servicebus` and `azure-servicemanagement-legacy`

This document covers the exceptions that you can get from the Azure SDK for Python, and will help
you decide what is worth retrying or what is a critical failure, depending on your application.

Every exception related to the service content will be referenced in the docstring of the method. For instance, for this 
:meth:`create_or_update<azure.mgmt.network.operations.NetworkSecurityGroupsOperations.create_or_update>` operation
you can see that you might receive a :exc:`CloudError<msrestazure:msrestazure.azure_exceptions.CloudError>`.

Where the service team provides no specific sub-classing, the basic exception you can expect from an operation is :exc:`CloudError<msrestazure:msrestazure.azure_exceptions.CloudError>`. 
In some situations however, the exceptions are specialized by package (see `azure-batch` package which uses :exc:`BatchErrorException<azure.batch.models.BatchErrorException>`).
If a specialized exception is used, it will always be a sub-class at some level of :exc:`ClientException<msrest.exceptions.ClientException>`.

Whether you should retry the same query or not for these exceptions depends on the service and the error content and cannot be generalized on this article.
For instance, an update to a SQL Database might be refused because you have another underlying operation (in this case you can retry); or a create request can be refused
because your selected name does not meet the pattern enforced by the server (in this case retry will never work). Use the `error` and `response` attributes of
:exc:`CloudError<msrestazure:msrestazure.azure_exceptions.CloudError>` to decide.

All these operations can also raise this set of generic exceptions that are defined in the :mod:`msrest.exceptions<msrest:msrest.exceptions>` module:

  - :exc:`AuthenticationError<msrest.exceptions.AuthenticationError>`: password invalid/expired, etc. Retry will likely not work.
  - :exc:`ClientRequestError<msrest.exceptions.ClientRequestError>`: `requests` library raised an exception (connection error, mostly HTTP level issues). Retry may work, though unlikely if your base_url is incorrect.
  - :exc:`DeserializationError<msrest.exceptions.DeserializationError>`: unexpected RestAPI answer. Retry will likely not work. Please create an issue on Github if you see this exception.
  - :exc:`HttpOperationError<msrest.exceptions.HttpOperationError>`: bad HTTP status code from Azure. See inner exception to decide if it's worth retrying.
  - :exc:`SerializationError<msrest.exceptions.SerializationError>`: unable to serialize your request. Your Python code didn't respect the expected model. Retry will never work. Please create an issue on Github if you see this exception and are 100% your parameters are correct.
  - :exc:`TokenExpiredError<msrest.exceptions.TokenExpiredError>`: please renew your credentials. Likely retry with new credentials will be ok.
  - :exc:`ValidationError<msrest.exceptions.ValidationError>`: client side check of your request failed. Fix your parameters with expected value. For instance, you didn't respect the regexp for the account name. This will never work on retry.

Asynchronous operation
++++++++++++++++++++++

An asynchronous operation is an operation that returns an :class:`AzureOperationPoller<msrestazure.azure_operation.AzureOperationPoller>`
(like :meth:`create_or_update<azure.mgmt.network.operations.NetworkSecurityGroupsOperations.create_or_update>`). Using this kind of operation
usually requires two lines:

.. code:: python
    
    async_poller = client.network_security_groups.create_or_update(myparameters)
    result = async_poller.result()

or, if this asynchronous operation is not returning a result:

.. code:: python
    
    async_poller = client.network_security_groups.create_or_update(myparameters)
    async_poller.wait()

Our recommendation is to surround both of the statements with the necessary try/except. More precisely, the first call might fail on the initial call
and the second one might fail during polling the status of the operation

.. important:: Old versions of the packages never failed on the first call, but this behavior was replaced by the one described and you should follow
               this pattern even for old packages.

Raw operation
+++++++++++++

All operations accept a `raw=True` parameter to indicate that the method must return the `requests.Response` instance directly.
All the above exceptions are still applicable, except for :exc:`DeserializationError<msrest.exceptions.DeserializationError>`, since the response will not be deserialized in this case.
