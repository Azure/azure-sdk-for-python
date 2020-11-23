# Release History

## 0.7.0 (2020-10-08)

**Features**

  - Supports 3.1 service version

## 0.6.0 (2020-05-18)

**Features**

  - Model Line has a new parameter language
  - Added operation ComputerVisionClientOperationsMixin.read
  - Added operation ComputerVisionClientOperationsMixin.get_read_result
  - Added operation ComputerVisionClientOperationsMixin.read_in_stream

**Breaking changes**

  - Parameter words of model Line is now required
  - Parameter bounding_box of model Line is now required
  - Parameter text of model Line is now required
  - Parameter confidence of model Word is now required
  - Removed operation ComputerVisionClientOperationsMixin.get_text_operation_result
  - Removed operation ComputerVisionClientOperationsMixin.get_read_operation_result
  - Removed operation ComputerVisionClientOperationsMixin.recognize_text_in_stream
  - Removed operation ComputerVisionClientOperationsMixin.recognize_text
  - Removed operation ComputerVisionClientOperationsMixin.batch_read_file
  - Removed operation ComputerVisionClientOperationsMixin.batch_read_file_in_stream
  - Model ReadOperationResult has a new signature

## 0.5.0 (2019-10-01)

**Features**

  - Model AdultInfo has a new parameter is_gory_content
  - Model AdultInfo has a new parameter gore_score

**Breaking changes**

  - Operation ComputerVisionClientOperationsMixin.analyze_image has a
    new signature
  - Operation
    ComputerVisionClientOperationsMixin.analyze_image_in_stream has a
    new signature
  - Operation ComputerVisionClientOperationsMixin.describe_image has a
    new signature
  - Operation
    ComputerVisionClientOperationsMixin.describe_image_in_stream has
    a new signature

## 0.4.0 (2019-06-27)

**Breaking changes**

  - "batch_read_file" and "batch_read_file_in_stream" have no
    "mode" parameter anymore

**Bugfix**

  - "bounding_box" now supports float numbers
  - Incorrect "Not Started" typo for state reporting

## 0.3.0 (2019-03-11)

**Features**

  - Model ImageAnalysis has a new parameter brands
  - Model ImageAnalysis has a new parameter objects
  - Model Word has a new parameter confidence

**Breaking changes**

  - Client ComputerVisionAPI has been renamed ComputerVisionClient
  - Parameter text of model Word is now required
  - Parameter bounding_box of model Word is now required

## 0.2.0 (2018-06-22)

**Features**

  - analyze_image now support 'en', 'es', 'ja', 'pt', 'zh' (including
    "in_stream" version of these operations)
  - describe_image/tag_image/analyze_image_by_domain now support
    the language parameter (including "in_stream" version of these
    operations)
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bug fixes**

  - Fix several invalid JSON description, that was raising unexpected
    exceptions (including OCRResult from bug #2614)

**Breaking changes**

  - recognize_text "detect_handwriting" boolean is now a "mode" str
    between 'Handwritten' and 'Printed'

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

## 0.1.0 (2018-01-23)

  - Initial Release
