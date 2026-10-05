# Grow Up Story for Generated SDKs

This quickstart will introduce how to grow up your generated code with customizations.

Handwritten patches (including `_patch.py`) extend generated SDK code without editing generated files directly. Follow the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) and the applicable generator's customization guidance; the [AutoRest Python customization guide](https://github.com/Azure/autorest.python/blob/main/docs/customizations.md) describes patching mechanics.

## Before You Customize

Before customizing generated code, consider whether your change should be made in TypeSpec (`client.tsp`) instead. TypeSpec customizations are cleaner and survive regeneration. See the [TypeSpec Client Customizations Reference](https://github.com/Azure/azure-sdk-tools/blob/main/eng/common/knowledge/customizing-client-tsp.md) for available decorators like `@@clientName`, `@@access`, etc.

Use code customizations (`_patch.py`) when TypeSpec cannot express the behavior you need.

## Before Adding or Changing a Patch

Apply this checklist to handwritten patches and customizations of generated Python SDK code, whether made manually or through customization tools:

1. **Identify generation inputs.** Record the generating tool and resolved version, service spec path and revision, configuration/options, and generation command. For TypeSpec, inspect `tsp-location.yaml`, `tspconfig.yaml`, and applicable emitter dependency/version records; for legacy AutoRest, inspect its generation configuration and generator version. Do not assume the current repository dependency version produced the affected code.
2. **Investigate the source of the behavior.** Distinguish an incorrect service spec/configuration from an emitter/generator defect or intentional SDK customization. When practical, use a minimal spec reproduction or regenerate with the identified inputs and inspect the unpatched output to establish evidence. Prefer correcting spec/configuration and regenerating, or fixing/reporting generator-wide defects in the responsible tool's upstream repository, instead of masking them in one SDK.
3. **Justify legitimate customizations.** Explain why the behavior belongs in the SDK's handwritten customization rather than the spec/configuration or generator.
4. **Track temporary generator workarounds.** For a confirmed emitter/generator bug, reference an existing upstream issue when available; otherwise document an explicit plan to report it. Add a regression test demonstrating the affected behavior and verifying the workaround, and state the removal/regeneration condition (for example, regenerate with a fixed generator version and remove the patch once the unpatched output passes the test).
5. **Document the diagnosis.** Include the inputs, expected versus actual behavior, reproduction/regeneration commands and results, and patch rationale in the PR description or nearby customization documentation. If investigation cannot be completed, record the blocker, what remains unverified, and the follow-up needed; do not claim an emitter/generator bug was ruled out without evidence.

This checklist is contributor and agent guidance, not automated enforcement.

## Key Concept: _patch.py

The `_patch.py` files at each level of the subfolders will be the entry point to customize the generated code.

For example, if you want to override a model, you will use the `_patch.py` file at the `models` level of your
generated code to override.

The main flow of the `_patch.py` file will be:

1. Import the generated object you wish to override.
2. Inherit from the generated object, and override its behavior with your desired code functionality
3. Include the name of your customized object in the `__all__` of the `_patch.py` file

To test that your behavior has been properly customized, please add tests for your customized code.
If you find that your customizations for an object are not being called, please make sure that
your customized object is included in the `__all__` of your `_patch.py` file.

The `_patch.py` file will never be removed during regeneration, so no worries about your customizations being
lost!

## Examples

- [Change Model Behavior](#change-model-behavior)
- [Change Operation Behavior](#change-operation-behavior)
- [Overload an Operation](#overload-an-operation)
- [Change Client Behavior](#change-client-behavior)
- [Add a Client Method](#add-a-client-method)

### Change Model Behavior

To override model behavior, you will work with the `_patch.py` file in the `models` folder of your generated code.

In the following example, we override the generated `Model`'s `input` parameter to accept both `str` and `datetime`,
instead of just `str`.

In this `_patch.py` file:

```
azure-sdk
│   README.md
│
└───azure
    └───sdk
        └───models
        │   _models.py # where the generated models are
        |   _patch.py # where we customize the models code
```

```python
import datetime
from typing import Union
from ._models import Model as ModelGenerated

class Model(ModelGenerated):

  def __init__(self, input: Union[str, datetime.datetime]):
    super().__init__(
      input=input.strftime("%d-%b-%Y") if isinstance(input, datetime.datetime) else input
    )

__all__ = ["Model"]
```

### Change Operation Behavior

To change an operation, you will import the generated operation group the operation is on. Then you can inherit
from the generated operation group and modify the behavior of the operation.

In the following example, the generated operation takes in a datetime input, and returns a datetime response.
We want to also allow users to input strings, and return a string response if users inputted a string.

In this `_patch.py` file:

```
azure-sdk
│   README.md
│
└───azure
    └───sdk
        └───operations
        │   _operations.py # where the generated operations are
        |   _patch.py # where we customize the operations code
```

```python
from typing import Union
import datetime
from ._operations import OperationGroup as OperationGroupGenerated

class OperationGroup(OperationGroupGenerated):

  def operation(self, input: Union[str, datetime.datetime]):
    response: datetime.datetime = super().operation(
        datetime.datetime.strptime(input, '%b %d %Y') if isinstance(input, str) else input
    )
    return response.strftime("%d-%b-%Y") if isinstance(input, str) else response


__all__ = ["OperationGroup"]
```

### Overload an Operation

You can also easily overload generated operations. For example, if you want users to be able to pass in the body parameter
as a positional-only single dictionary, or as splatted keyword arguments, you can inherit and override the operation on the operation group
in the `_patch.py` file in the `operations` subfolders.

In this `_patch.py` file:

```
azure-sdk
│   README.md
│
└───azure
    └───sdk
        └───operations
        │   _operations.py # where the generated operations are
        |   _patch.py # where we customize the operations code
```

```python
from typing import overload, Dict, Any
from ._operations import OperationGroup as OperationGroupGenerated

class OperationGroup(OperationGroupGenerated):

    @overload
    def operation(self, body: Dict[str, Any], /, **kwargs: Any):
        """Pass in the body as a positional only parameter."""

    @overload
    def operation(self, *, foo: str, bar: str, **kwargs: Any):
        """Pass in the body as splatted keyword only arguments."""

    def operation(self, *args, **kwargs):
        """Base operation for the two overloads"""
        if not args:
            args.append({"foo": kwargs.pop("foo"), "bar": kwargs.pop("bar")})
        return super().operation(*args, **kwargs)

__all__ = ["OperationGroup"]
```

### Change Client Behavior

In this example, we add our own special token, and change the authentication policy behavior for a client.

In this `_patch.py` file:

```
azure-sdk
│   README.md
│
└───azure
    └───sdk
        │   _service_client.py # where the generated service client is
        |   _patch.py # where we customize the client code
        └───operations
        └───models
```

```python
from typing import Union

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import TokenCredential

from ._service_client import ServiceClient as ServiceClientGenerated

class MyCredential:

    def __init__(self, key: str, region: str) -> None:
        self.key = key
        self.region = region


class MyAuthenticationPolicy(SansIOHTTPPolicy):

    def __init__(self, credential: MyCredential):
        self.credential = credential

    def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Ocp-Apim-Subscription-Key"] = self.credential.key
        request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.credential.region

class ServiceClient(ServiceClientGenerated):

    def __init__(self, endpoint: str, credential: Union[TokenCredential, MyCredential], **kwargs):
        if isinstance(credential, MyCredential):
            # if it's our credential, we default to our authentication policy.
            # Otherwise, we use the default
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = MyAuthenticationPolicy(credential)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            **kwargs
        )

__all__ = ["ServiceClient"]
```

### Add a Client Method

Similar to models and operations, you can override client behavior in a `_patch.py` file, this time
at the root of the sdk.

Here, we will be adding an alternate form of authentication on the client, class method `from_connection_string`.

In this `_patch.py` file:

```
azure-sdk
│   README.md
│
└───azure
    └───sdk
        │   _service_client.py # where the generated service client is
        |   _patch.py # where we customize the client code
        └───operations
        └───models
```

```python
from typing import Any
from azure.core.credentials import AzureKeyCredential
from ._service_client import ServiceClient as ServiceClientGenerated

class ServiceClient(ServiceClientGenerated):

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs: Any):
        parsed_connection_string = _parse_connection_string(connection_string) # parsing function you've defined
        return cls(
            credential=AzureKeyCredential(parsed_connection_string.pop("accesskey")),
            endpoint=parsed_connection_string.pop("endpoint")
        )

__all__ = ["ServiceClient"]
```

## Postprocessing (REMOVED)

There is no need to run the postprocessing script anymore, since we deal with all typing issues at generation time. As such, support for this command has been removed
