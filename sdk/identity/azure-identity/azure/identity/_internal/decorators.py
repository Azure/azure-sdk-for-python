# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import json
import base64

from six import raise_from
from azure.core.exceptions import ClientAuthenticationError

from .utils import within_credential_chain


_LOGGER = logging.getLogger(__name__)


def log_get_token(class_name):
    """Adds logging around get_token calls.

    :param str class_name: required for the sake of Python 2.7, which lacks an easy way to get the credential's class
        name from the decorated function
    """

    def decorator(fn):
        qualified_name = class_name + ".get_token"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                token = fn(*args, **kwargs)
                _LOGGER.log(
                    logging.DEBUG if within_credential_chain.get() else logging.INFO, "%s succeeded", qualified_name
                )
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    try:
                        base64_meta_data = token.token.split(".")[1].encode("utf-8") + b'=='
                        json_bytes = base64.decodebytes(base64_meta_data)
                        json_string = json_bytes.decode('utf-8')
                        json_dict = json.loads(json_string)
                        upn = json_dict.get('upn', 'unavailableUpn')
                        log_string = '[Authenticated account] Client ID: {}. Tenant ID: {}. User Principal Name: {}. ' \
                                     'Object ID (user): {}'.format(json_dict['appid'],
                                                                   json_dict['tid'],
                                                                   upn,
                                                                   json_dict['oid']
                                                                   )
                        _LOGGER.debug(log_string)
                    except Exception:     # pylint: disable=broad-except
                        _LOGGER.debug("Fail to log the account information")
                return token
            except Exception as ex:   # pylint: disable=broad-except
                _LOGGER.log(
                    logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                    "%s failed: %s",
                    qualified_name,
                    ex,
                    exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                )
                raise

        return wrapper

    return decorator


def wrap_exceptions(fn):
    """Prevents leaking exceptions defined outside azure-core by raising ClientAuthenticationError from them."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientAuthenticationError:
            raise
        except Exception as ex:  # pylint:disable=broad-except
            auth_error = ClientAuthenticationError(message="Authentication failed: {}".format(ex))
            raise_from(auth_error, ex)

    return wrapper
