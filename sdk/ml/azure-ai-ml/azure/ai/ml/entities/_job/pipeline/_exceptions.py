# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._ml_exceptions import MlException, ErrorCategory, ErrorTarget


class UserErrorException(MlException):
    """Exception raised when invalid or unsupported inputs are provided."""

    def __init__(self, message, no_personal_data_message=None, error_category=ErrorCategory.USER_ERROR):
        super().__init__(
            message=message,
            target=ErrorTarget.PIPELINE,
            no_personal_data_message=no_personal_data_message,
            error_category=error_category,
        )


class CannotSetAttributeError(UserErrorException):
    """Exception raised when a user try setting attributes of inputs/outputs."""

    def __init__(self, object_name):
        msg = "It is not allowed to set attribute of %r." % object_name
        super(CannotSetAttributeError, self).__init__(
            message=msg, no_personal_data_message="It is not allowed to set attribute of object."
        )


class UnsupportedParameterKindError(UserErrorException):
    """Exception raised when a user try setting attributes of inputs/outputs."""

    def __init__(self, func_name):
        msg = "%r: dsl pipeline does not accept *args or **kwargs as parameters." % func_name
        super(UnsupportedParameterKindError, self).__init__(message=msg, no_personal_data_message=msg)


class KeywordError(UserErrorException):
    """Super class of all type keyword error."""

    def __init__(self, message, no_personal_data_message=None):
        super().__init__(message=message, no_personal_data_message=no_personal_data_message)


class UnexpectedKeywordError(KeywordError):
    """Exception raised when an unexpected keyword parameter is provided in dynamic functions."""

    def __init__(self, func_name, keyword, keywords=None):
        message = "%s() got an unexpected keyword argument %r" % (func_name, keyword)
        message += ", valid keywords: %s." % ", ".join("%r" % key for key in keywords) if keywords else "."
        super().__init__(message=message, no_personal_data_message=message)


class UnexpectedAttributeError(KeywordError, AttributeError):
    """Exception raised when an unexpected keyword is invoked by attribute, e.g. inputs.invalid_key"""

    def __init__(self, keyword, keywords=None):
        message = "Got an unexpected attribute %r" % keyword
        message += ", valid attributes: %s." % ", ".join("%r" % key for key in keywords) if keywords else "."
        KeywordError.__init__(self, message=message, no_personal_data_message=message)


class MissingPositionalArgsError(KeywordError):
    """Exception raised when missing positional keyword parameter in dynamic functions."""

    def __init__(self, func_name, missing_args):
        message = "%s() missing %d required positional argument(s): %s." % (
            func_name,
            len(missing_args),
            ", ".join("%r" % key for key in missing_args) if missing_args else ".",
        )
        super().__init__(message=message, no_personal_data_message=message)


class TooManyPositionalArgsError(KeywordError):
    """Exception raised when too many positional arguments is provided in dynamic functions."""

    def __init__(self, func_name, min_number, max_number, given_number):
        message = "%s() takes %s positional argument but %d were given." % (
            func_name,
            min_number if min_number == max_number else f"{min_number} to {max_number}",
            given_number,
        )
        super().__init__(message=message, no_personal_data_message=message)


class MultipleValueError(KeywordError):
    """Exception raised when giving multiple value of a keyword parameter in dynamic functions."""

    def __init__(self, func_name, keyword):
        message = "%s() got multiple values for argument %r." % (func_name, keyword)
        super().__init__(message=message, no_personal_data_message=message)


class UnsupportedOperationError(UserErrorException):
    """Exception raised when specified operation is not supported."""

    def __init__(self, operation_name):
        message = "Operation %s is not supported." % operation_name
        super().__init__(message=message, no_personal_data_message=message)


class DSLComponentDefiningError(UserErrorException):
    """This error indicates that the user define a dsl.component in an incorrect way."""

    def __init__(self, cause):
        """Init the error with the cause which causes the wrong dsl.component."""
        msg = "Defining the component failed due to {}."
        super().__init__(message=msg.format(cause), no_personal_data_message=msg.format("[cause]"))


# region dsl component
class NoDslComponentError(UserErrorException):
    """Exception when no valid dsl component found in specific file."""

    def __init__(self, file, name=None):
        """Error message inits here."""
        if name:
            msg = "No dsl.component with name {} found in {}."
            super().__init__(message=msg.format(name, file), no_personal_data_message=msg.format("[name]", "[file]"))
        else:
            msg = "No dsl.component found in {}."
            super().__init__(message=msg.format(file), no_personal_data_message=msg.format("[file]"))


class RequiredComponentNameError(UserErrorException):
    """Exception when multiple dsl.components are found and no component name specified."""

    def __init__(self, file):
        """Error message inits here."""
        msg = "More than one dsl.component found in {}, '--name' parameter is required."
        super().__init__(message=msg.format(file), no_personal_data_message=msg.format("[file]"))


class TooManyDSLComponentsError(UserErrorException):
    """Exception when multiple dsl.components are found in single component entry."""

    def __init__(self, count, file, component_name=None):
        """Error message inits here."""
        if not component_name:
            msg = "Only one dsl.component is allowed per file, {} found in {}".format(count, file)
            no_personal_data_msg = "Only one dsl.component is allowed per file, {} found in {}".format(count, "[file]")
        else:
            msg = "More than one dsl.component with name %r found in %r, count %d." % (component_name, file, count)
            no_personal_data_msg = "More than one dsl.component with name %r found in %r, count %d." % (
                "[component_name]",
                "[file]",
                count,
            )
        super().__init__(message=msg, no_personal_data_message=no_personal_data_msg)


class RequiredParamParsingError(UserErrorException):
    """This error indicates that a parameter is required but not exists in the command line."""

    def __init__(self, name, arg_string):
        """Init the error with the parameter name and its arg string."""
        msg = "'{}' cannot be None since it is not optional. Please make sure command option '{}' exists."
        super().__init__(
            message=msg.format(name, arg_string), no_personal_data_message=msg.format("[name]", "[arg_string]")
        )
