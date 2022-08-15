# Docstrings and Type Hints

All public methods should have docstrings to document the parameters, keywords, exceptions raised, and return types for each method. Models and clients should also document properties, instance variables, and class variables.

* [Docstrings](#docstrings)
    * [Method Docstrings](#method_docstrings)
    * [Model and Client Docstrings](#model_and_client_docstrings)
* [Type Hints](#type_hints)
    * [Type Hints for Python 2.7 and 3.5+](#type_hints_for_python_2.7_and_3.5+)
    * [Type Hints for Python 3.5+](#type_hints_for_python_3.5+)

## Docstrings

Docstrings are noted by the Python long-string `"""<docstring>"""`. When adding docstrings the `~` can be optionally added to the front of a custom model, this will only display the actual model name in the documentation. For example a type that looks like `azure.data.tables.TableEntity` will display the entire path in the documentation, but `~azure.data.tables.TableEntity` will only display `TableEntity` in the documentation. Additionally, adding the wrapper `` :class:`~azure.data.tables.TableEntity` `` will display only `TableEntity` formatted in monospace font. These documentation methods will also create direct links to the type documentation. Both of these capabilities are optional and can only be used in the two-line format described below.

### Method Docstrings

A method docstring is annotated by the Python long-string `"""<docstring>"""` right after the method definition. The convention is a short line ending with a period, two new lines, followed by a longer description. Below is an example of a full docstring from `azure-ai-formrecognizer`:
```python
    @distributed_trace
    def begin_training(self, training_files_url, use_training_labels, **kwargs):
        # type: (str, bool, Any) -> LROPoller[CustomFormModel]
        """Create and train a custom model.

        The request must include a `training_files_url` parameter that is an
        externally accessible Azure storage blob container URI (preferably a Shared Access Signature URI). Note that
        a container URI (without SAS) is accepted only when the container is public.
        Models are trained using documents that are of the following content type - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff', or 'image/bmp'. Other types of content in the container is ignored.

        :param str training_files_url: An Azure Storage blob container's SAS URI. A container URI (without SAS)
            can be used if the container is public. For more information on setting up a training data set, see:
            https://docs.microsoft.com/azure/cognitive-services/form-recognizer/build-training-data-set
        :param bool use_training_labels: Whether to train with labels or not. Corresponding labeled files must
            exist in the blob container if set to `True`.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            training. For example, when using a Azure storage blob URI, use the prefix to restrict sub
            folders for training.
        :keyword include_subfolders: A flag to indicate if subfolders within the set of prefix folders
            will also need to be included when searching for content to be preprocessed. Not supported if
            training with labels.
        :paramtype include_subfolders: bool
        :keyword str model_name: An optional, user-defined name to associate with your model.
        :keyword continuation_token: A continuation token to restart a poller from a saved state.
        :paramtype continuation_token: str
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.CustomFormModel`.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.formrecognizer.CustomFormModel]
        :raises ~azure.core.exceptions.HttpResponseError:
            Note that if the training fails, the exception is raised, but a model with an
            "invalid" status is still created. You can delete this model by calling :func:`~delete_model()`

        .. versionadded:: v2.1
            The *model_name* keyword argument

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_train_model_without_labels.py
                :start-after: [START training]
                :end-before: [END training]
                :language: python
                :dedent: 8
                :caption: Training a model (without labels) with your custom forms.
        """
        ...
```

The first portion of this docstring is a general description of what the method does. Following the general description of the method is a **required new line** and then documentation for each of the parameters, optional keyword arguments, returned objects, and potentially raised errors.

Positional parameters can be documented in one-line or two-lines. Both options can be used in a single docstring for documenting different parameters without issue.
1. This option works best for parameters that are one of the basic types (`str`, `int`, `bool`, `bytes`, `float`, etc.)
```python
:param <type> <param_name>: <Description of the parameter>
```
2. This option works best for parameters that use custom models or have many different options
```python
:param <param_name>: <Description of the parameter>
:type <param_name>: <param_type>
```

Optional keyword arguments can be documented in one-line or two-lines. Both options can be used in a single docstring for documenting different keywords without issue. Keywords includes kwargs and in Python 3 code only, parameters after `*` character.
1. This option works best for keyword args that are one of the basic types (`str`, `int`, `bool`, `bytes`, `float`, etc.)
```python
:keyword <type> <keyword_name>: <Description of the keyword>
```
2. This option works best for keyword that use custom models or have many different options
```python
:keyword <keyword_name>: <Description of the keyword>
:paramtype <keyword_name>: <keyword_type>
```

The returned object is documented on two lines, the first describing what the returned object is and the second describing what the returned type is.
```python
"""
:return: <Description of the returned object>
:rtype: <Type of the returned object>
"""
```

Finally, describe the possible errors raised by a method:
```python
:raises <error1>, <error2>, or <error3>: <description>
```

All of the above information needs to be added for each public method and there **needs to be a newline after the above docstrings**. There are additional options for including examples and version specific additions.

For adding a version specific change use the `versionadded` docstring:
```
.. versionadded:: <version_number>

```

Additional sphinx directives are documented [here](https://review.docs.microsoft.com/help/onboard/admin/reference/python/documenting-api?branch=master#supported-sphinx-directives)

### Model and Client Docstrings

For documenting the properties of a model or client, include a docstring right after the `__init__` method or immediately after the class declaration

Here is an example in `azure-ai-textanalytics`:
```python
class DetectedLanguage(DictMixin):
    """DetectedLanguage contains the predicted language found in text,
    its confidence score, and its ISO 639-1 representation.

    :ivar name: Long name of a detected language (e.g. English,
        French).
    :vartype name: str
    :ivar iso6391_name: A two letter representation of the detected
        language according to the ISO 639-1 standard (e.g. en, fr).
    :vartype iso6391_name: str
    :ivar confidence_score: A confidence score between 0 and 1. Scores close
        to 1 indicate 100% certainty that the identified language is true.
    :vartype confidence_score: float
    """
```

The properties of a model should be documented with the `ivar` docstring:
```
:ivar <property_name>: <description>
:vartype <property_name>: <type>
```

Models that are used as a positional or keyword argument for methods that make service calls should have docstrings that expand past `ivars`. Below is an example of a model from `azure-ai-translation-document` that has positional and keyword argument parameters documented.

```python
class DocumentTranslationInput(object):  # pylint: disable=useless-object-inheritance
    # pylint: disable=C0301
    """Input for translation. This requires that you have your source document or
    documents in an Azure Blob Storage container. Provide a SAS URL to the source file or
    source container containing the documents for translation. The source document(s) are
    translated and written to the location provided by the TranslationTargets.

    :param str source_url: Required. Location of the folder / container or single file with your
        documents.
    :param targets: Required. Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified.
    :type targets: list[~azure.ai.translation.document.TranslationTarget]
    :keyword str source_language_code: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :keyword storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.

    :ivar str source_url: Required. Location of the folder / container or single file with your
        documents.
    :ivar targets: Required. Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified.
    :vartype targets: list[~azure.ai.translation.document.TranslationTarget]
    :ivar str source_language_code: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :ivar str prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :ivar str suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :ivar storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :vartype storage_type: str or ~azure.ai.translation.document.StorageInputType
    :ivar str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """
```

Positional parameters and keyword arguments are documented in the exact same way as a client method would be, using the `param` and `keyword` descriptors. Although not required, a new line between `param` and `keyword` descriptors helps to separate the docstring into logically separated groups.


## Type Hints

### Type Hints for Python 2.7 and 3.5+

Python 2.7 does not support in-line type hints, the type hints for all sync code will have to adhere to type-hints in comments only. On all public methods include a type-hint by using the `# type: (...) -> (...)` format:
```python
def add(num1, num2):
    # type: (int, int) -> int
    return num1 + num2
```
The spacing in type hints is important, there must be a space between "#" and "type", after the semicolon, and before and after the "->". If the type hint is not properly formatted API View will not recognize them.

Here is a more complex example from `azure-ai-textanalytics`
```python
from typing import List, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ._models import TextDocumentInput, RecognizeEntitiesResult

def recognize_entities(
    self,
    documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
    **kwargs  # type: Any
):
    # type: (...) -> List[Union[RecognizeEntitiesResult, DocumentError]]
```

If a parameter can be one of many types use the `Union` type to describe all possible options. Types such as dict, list, and tuple have to be imported from the `typing` module as demonstrated at the top of the snippet. For the complex types (Dict, List, Tuple), the inner type has to be declared as well. For example, a list of strings is `List[str]`, a dictionary mapping strings to many different types of objects can be described as `Dict[str, object]`. Custom types have to be imported under a type checking conditional, importing `TYPE_CHECKING` from the `typing` module and only importing the custom models within this `if` statement.

### Type Hints for Python 3.5+

The async models and clients are only valid in Python 3.5+ which allows for the use of in-line type hints. A simple example follows:
```python
def add(num1: int, num2: int) -> int:
    return num1 + num2
```

Here is a more complex example from `azure-ai-textanalytics`
```python
from typing import List, Dict, Union
from ._models import TextDocumentInput, RecognizeEntitiesResult

def recognize_entities(
    self,
    documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
    **kwargs: Any
) -> List[Union[RecognizeEntitiesResult, DocumentError]]:
```
Note that in the in-line type hints the custom models do not to be guarded by an `if TYPE_CHECKING` conditional. These custom models must be included in imports or the program will fail on the type not being found. Do not use `dict[str,list[str]]`, always use the upper case version from the `typing` module, instead do `Dict[str, List[str]]`.
