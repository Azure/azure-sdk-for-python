# Samples, Snippets, and How-To Guides

Developers like to learn by looking at code, and so the Azure SDK comes with a myriad of code samples in the form of short code snippets, sample applications, and how-to guides. This document describes where to find all these resources.

## Structure of the Repository
The Azure SDK repository is organized in the following folder structure, with the main sample locations highlighted using **bold** font.

- `/sdk` (folder containing sources for all SDK packages)
  - `/<service>` (e.g. storage)
    - `/<package>` (e.g. `azure-storage-blob`)
      - **`README.md`** (package READMEs contain "hello world" code snippets)
      - **`/samples`** (package-specific samples using synchronous code)
        - **`/async_samples`** (package-specific samples using asynchronous code)
        - **`README.md`** (sample README contains outline and how to run information)
      - `/azure`
      - `/tests`

##  Getting Started (a.k.a. `Hello World`) README Examples
Each package folder contains a package-specific `README.md` file. Most of these `README` files contain `Hello World` code samples illustrating basic usage of the APIs contained in the package.
Note that the package-level README should not include samples for every API available in the client library -- it is meant to highlight the champion scenarios, or most common scenarios used by our customers.

[README examples][blob_readme]

## Package Samples
Each package folder contains a subfolder called `samples` with additional code samples which are runnable `.py` files. Please read the Python sample guidelines to understand the requirements for a sample: [Sample Guidelines][python_sample_guidelines].
Each sample scenario should include an asynchronous equivalent under a separate file with the file name suffix `_async.py`. Async samples can be organized under a separate directory, i.e. `samples/async_samples`.

A sample should start with a [header][sample_header] that explains what the sample will demonstrate and any set-up necessary to run it, including environment variables which must be set. 
The code for the sample should be runnable by invoking `python sample.py` and demonstrate the intended scenario in one file which can be copy/pasted easily into an IDE.

[Sample sync example][example_sample_sync]

[Sample async example][example_sample_async]

## Package Sample README
A samples-level README provides a high-level overview of the provided samples and how to get started with running them in a local environment. 

[Sample README example][example_samples_readme]

The Samples README also contains [metadata][metadata_example] to help publish our samples to the [Microsoft Samples browser][samples_browser].
Note that the metadata under `products` must match an existing product slug found [here][product_slug]. See [here][request_product_slug] for requesting a new product slug.

## Capturing code snippets in reference documentation
Code snippets from samples can be captured as [examples][qa_example] in our reference documentation.
To do this, place `# [START <keyword>]` and `# [END <keyword>]` comments which span the lines you want to show up in the reference documentation example.
Note that the <keyword> used should be unique across all sync/async samples added to a client library.

[Sample Example][qa_code_snippet]

The given `START`/`END` keywords can be used in a [sphinx literalinclude][sphinx] directive in the docstring where the code snippet should be rendered in the reference documentation.

[Literalinclude example][literalinclude]

The rendered code snippets are sensitive to the indentation in the sample file. Adjust the `dedent` accordingly to ensure the sample is captured accurately and not accidentally trimmed.
You can preview how published reference documentation will look by running [tox][tox]: `tox -e sphinx -c ../../../eng/tox/tox.ini`.

## Test run samples in CI live tests
Per the [Python guidelines][snippet_guidelines], sample code and snippets should be test run in CI to ensure they remain functional. Samples should be run in the package's live test pipeline which is scheduled to run daily.
To ensure samples do get tested as part of regular CI runs, add these [lines][live_tests] to the package's tests.yml. 

You can test this CI step locally first, by utilizing [tox][tox] and running `tox -e samples -c ../../../eng/tox/tox.ini` at the package-level.

The `Test Samples` step in CI will rely on the resources provisioned and environment variables used for running the package's tests.

## Sample Applications
Sometimes we want to illustrate how several APIs or even packages work together in a context of a more complete program. For these cases, we created sample applications that you can look at, download, compile, and execute. These application samples are located on 
[https://learn.microsoft.com/samples/browse/][msft_samples].

## How-to Guides
For general how-to with the Python SDK, see the [Azure SDK for Python Overview][python_sdk_overview] docs.

## More Information

[Python Guidelines][python_guidelines]

[How to Document an SDK client library (Microsoft Internal)][document_sdk] 

<!-- LINKS -->

[python_sample_guidelines]: https://azure.github.io/azure-sdk/python_design.html#samples
[blob_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/README.md#examples
[sample_header]: https://github.com/Azure/azure-sdk-for-python/blob/7b3dfdca0658f6a4706654556d3142b4bce2b0d1/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation.py#L6-L26
[metadata_example]: https://github.com/Azure/azure-sdk-for-python/blob/7b3dfdca0658f6a4706654556d3142b4bce2b0d1/sdk/translation/azure-ai-translation-document/samples/README.md?plain=1#L1-L10
[samples_browser]: https://learn.microsoft.com/samples/browse/
[product_slug]: https://review.learn.microsoft.com/help/platform/metadata-taxonomies?branch=main#product
[request_product_slug]: https://review.learn.microsoft.com/help/platform/metadata-request-changes?branch=main
[qa_example]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-questionanswering/1.1.0/azure.ai.language.questionanswering.html#azure.ai.language.questionanswering.QuestionAnsweringClient.get_answers_from_text
[qa_code_snippet]: https://github.com/Azure/azure-sdk-for-python/blob/7b3dfdca0658f6a4706654556d3142b4bce2b0d1/sdk/cognitivelanguage/azure-ai-language-questionanswering/azure/ai/language/questionanswering/_operations/_patch.py#L244-L251
[literalinclude]: https://github.com/Azure/azure-sdk-for-python/blob/7b3dfdca0658f6a4706654556d3142b4bce2b0d1/sdk/cognitivelanguage/azure-ai-language-questionanswering/azure/ai/language/questionanswering/_operations/_patch.py#L244-L251
[snippet_guidelines]: https://azure.github.io/azure-sdk/python_design.html#code-snippets
[live_tests]: https://github.com/Azure/azure-sdk-for-python/blob/7b3dfdca0658f6a4706654556d3142b4bce2b0d1/sdk/translation/tests.yml#L13-L14
[tox]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox
[msft_samples]: https://learn.microsoft.com/samples/browse/
[python_guidelines]: https://azure.github.io/azure-sdk/python_design.html
[document_sdk]: https://review.learn.microsoft.com/help/platform/reference-document-sdk-client-libraries?branch=main
[python_sdk_overview]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-overview
[example_samples_readme]: https://github.com/Azure/azure-sdk-for-python/blob/b191c54ba9e6001a6f896d05bafd119dbe82ce63/sdk/translation/azure-ai-translation-document/samples/README.md
[example_sample_sync]: https://github.com/Azure/azure-sdk-for-python/blob/b191c54ba9e6001a6f896d05bafd119dbe82ce63/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation.py
[example_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_begin_translation_async.py
[sphinx]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude