# Docstrings and Type Hints

All public methods should have docstrings to document the parameters, keywords, and return types for each method. Models and clients should also document properties, instance variables, and class variables.

* [Docstrings](#docstrings)
    * [Method Docstrings](#method_docstrings)
    * [Model and Client Docstrings](#Model_and_Client_Docstrings)
* [Type Hints](#type_hints)
    * [Type Hints for Python 2.7 and 3.5+](#type_hints_for_python_2.7_and_3.5+)
    * [Type Hints for Python 3.5+](#type_hints_for_python_3.5+)

## Docstrings

Docstrings are noted by the Python long-string `"""<docstring>"""`. When adding docstrings the `~` can be optionally added to the front of a custom model, this will only display the actual model name in the documentation. For example a type that looks like `azure.data.tables.TableEntity` will display the entire path in the documentation, but `~azure.data.tables.TableEntity` will only display `TableEntity` in the documentation. Additionally, adding the wrapper `` :class:`~azure.data.tables.TableEntity` `` will display only `TableEntity` formatted in monospace font. Both of these capabilities are optional and can only be used in the two-line format described below.

### Method Docstrings

A method docstring is annotated by the Python long-string `"""<docstring>"""` right after the method definition. Below is an example of a full docstring from `azure-ai-formrecognizer`:
```python
    @distributed_trace
    def begin_training(self, training_files_url, use_training_labels, **kwargs):
        # type: (str, bool, Any) -> LROPoller[CustomFormModel]
        """Create and train a custom model. The request must include a `training_files_url` parameter that is an
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
        :keyword bool include_subfolders: A flag to indicate if subfolders within the set of prefix folders
            will also need to be included when searching for content to be preprocessed. Not supported if
            training with labels.
        :keyword str model_name: An optional, user-defined name to associate with your model.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
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

Required parameters can be documented in one-line or two-lines. Both options can be used in a single docstring for documenting different parameters without issue.
1. This option works best for parameters that are one of the basic types (`str`, `int`, `bool`, `bytes`, `float`, etc.)
```python
:param <type> <param_name>: <Description of the parameter>
```
2. This option works best for parameters that use custom models or have many different options
```python
:param <param_name>: <Description of the parameter>
:type <param_name>: <param_type>
```

Optional keyword arguments can in one-line or two-lines. Both options can be used in a single docstring for documenting different keywords without issue.
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
.. versionadded

### Model and Client Docstrings

## Type Hints

### Type Hints for Python 2.7 and 3.5+

### Type Hints for Python 3.5+
