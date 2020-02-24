# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import functools
import logging
import sys
from threading import Lock

from .base import ReplayableTest
from .utilities import create_random_name, is_text_payload, trim_kwargs_from_test_function
from .recording_processors import RecordingProcessor
from .exceptions import AzureNameError

_logger = logging.getLogger("preparer")
_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
_logger.addHandler(handler)

# Core Utility


class AbstractPreparer(object):
    _cache_lock = Lock()
    _resource_cache = {}
    _cache_pending_deletes = {}
    def __init__(self, name_prefix, name_len, disable_recording=False):
        self.name_prefix = name_prefix
        self.name_len = name_len
        self.resource_moniker = None
        self.resource_random_name = None
        self.test_class_instance = None
        self.live_test = False
        self.disable_recording = disable_recording
        self._cache_key = (self.__class__.__name__,)
        self._use_cache = False
        self._aggregate_cache_key = None

    def _prepare_create_resource(self, test_class_instance, fn, **kwargs):
        self.live_test = not isinstance(test_class_instance, ReplayableTest)
        self.test_class_instance = test_class_instance

        if self.live_test or test_class_instance.in_recording:
            resource_name = self.random_name
            if not self.live_test and isinstance(self, RecordingProcessor):
                test_class_instance.recording_processors.append(self)
        else:
            resource_name = self.moniker

        # If a child is cached we must use the same cached resource their equivalent parent did so all the deps line up
        try:
            child_is_cached = getattr(fn, '__use_cache')
            # Note: If it is ever desired to make caching inferred, remove this if/throw.
            # This ensures that a user must _very specifically say they want caching_ on an item and all parents.
            if not self._use_cache:
                raise Exception("""Preparer exception for test {}:\n Child preparers are cached, but parent {} is not.
You must specify use_cache=True in the preparer decorator""".format(test_class_instance, self.__class__.__name__))
            self._use_cache |= child_is_cached
            _logger.debug("Detected transient cache for %s: %s", self.__class__.__name__, child_is_cached)
        except AttributeError: # If the child callable doesn't declare itself cached, we can move on.
            pass

        # We must use a cache_key that includes our parents, so that we get a cached stack
        # matching the desired resource stack. (e.g. if parent resource has specific settings)
        try:
            aggregate_cache_key = (self._cache_key, kwargs['__aggregate_cache_key'])
        except KeyError: # If we're at the root of the cache stack, start with our own key.
            aggregate_cache_key = self._cache_key
        kwargs['__aggregate_cache_key'] = aggregate_cache_key
        self._aggregate_cache_key = aggregate_cache_key
        _logger.debug("Aggregate cache key: %s", aggregate_cache_key)

        # If cache is enabled, and the cached resource exists, use it, otherwise create and store.
        if self._use_cache and aggregate_cache_key in AbstractPreparer._resource_cache:
            _logger.debug("Using cached resource for %s", self.__class__.__name__)
            with self._cache_lock:
                parameter_update = AbstractPreparer._resource_cache[aggregate_cache_key]
        else:
            _logger.debug("Creating resource %s for %s", resource_name, self.__class__.__name__)
            with self.override_disable_recording():
                retries = 4
                for i in range(retries):
                    try:
                        parameter_update = self.create_resource(
                            resource_name,
                            **kwargs
                        )
                        _logger.debug("Successfully created resource %s", resource_name)
                        break
                    except AzureNameError:
                        if i == retries - 1:
                            raise
                        self.resource_random_name = None
                        resource_name = self.random_name
                    except Exception as e:
                        _logger.error("Failed to create resource: %s \nResponse: %s",
                            getattr(e, 'inner_exception', e), getattr(e, 'response', None))
                        raise
        if self._use_cache:
            _logger.debug("Storing cached resource for %s", self.__class__.__name__)
            with self._cache_lock:
                AbstractPreparer._resource_cache[aggregate_cache_key] = parameter_update

        if parameter_update:
            kwargs.update(parameter_update)

        return resource_name, kwargs


    def __call__(self, fn):
        def _preparer_wrapper(test_class_instance, **kwargs):
            _logger.debug("Entering preparer wrapper for %s and test %s",
                self.__class__.__name__, str(test_class_instance))

            resource_name, kwargs = self._prepare_create_resource(test_class_instance, fn, **kwargs)

            trim_kwargs_from_test_function(fn, kwargs)

            try:
                test_class_instance._delay_removal = False # pylint: disable=protected-access
                fn(test_class_instance, **kwargs)
                if self._use_cache: # If we're cached, stop things above us (e.g. RG) from deleting.
                    test_class_instance._delay_removal = True # pylint: disable=protected-access
            finally:              
                def _deferred_delete():
                    _logger.debug("Running deferred delete for %s", self)
                    self.remove_resource_with_record_override(resource_name, **kwargs)
                # If we use cache we delay deletion for the end.
                # This won't guarantee deletion order, but it will guarantee everything delayed
                # does get deleted, in the worst case by getting rid of the RG at the top.
                if self._use_cache:
                    # Only the first occurance though; since they point to the same underlying, and the
                    # latter cache-fetched-instances didn't actually initialize ARM clients to be able to delete.
                    if self._aggregate_cache_key not in AbstractPreparer._cache_pending_deletes:
                        with self._cache_lock:
                            AbstractPreparer._cache_pending_deletes[self._aggregate_cache_key] = _deferred_delete
                elif test_class_instance._delay_removal: # pylint: disable=protected-access
                    # If a child is specifying a cache but we aren't, raise an exception.
                    # If it were ever desired to do implied caching, one would simply add a deferred delete here.
                    # raise Exception("Preparer Error: If a child resource is cached, parents must also be cached")
                    if self._aggregate_cache_key not in AbstractPreparer._cache_pending_deletes:
                        with self._cache_lock:
                            AbstractPreparer._cache_pending_deletes[self._aggregate_cache_key] = _deferred_delete
                else:
                    # Russian Doll - the last declared resource to be deleted first.
                    self.remove_resource_with_record_override(resource_name, **kwargs)

        # _logger.debug("Setting up preparer stack for {}".format(self.__class__.__name__))
        setattr(_preparer_wrapper, '__is_preparer', True)
        # Inform the next step in the chain (our parent) that we're cached.
        if self._use_cache or getattr(fn, '__use_cache', False):
            setattr(_preparer_wrapper, '__use_cache', True)
        functools.update_wrapper(_preparer_wrapper, fn)
        return _preparer_wrapper

    @contextlib.contextmanager
    def override_disable_recording(self):
        if hasattr(self.test_class_instance, 'disable_recording'):
            orig_enabled = self.test_class_instance.disable_recording
            self.test_class_instance.disable_recording = self.disable_recording
            yield
            self.test_class_instance.disable_recording = orig_enabled
        else:
            yield

    @property
    def moniker(self):
        if not self.resource_moniker:
            self.test_class_instance.test_resources_count += 1
            self.resource_moniker = '{}{:06}'.format(self.name_prefix,
                                                     self.test_class_instance.test_resources_count)
        return self.resource_moniker

    def create_random_name(self):
        return create_random_name(self.name_prefix, self.name_len)

    @property
    def random_name(self):
        if not self.resource_random_name:
            self.resource_random_name = self.create_random_name()
        return self.resource_random_name

    # The only other design idea I see that doesn't require each preparer to be instrumented
    # would be to have a decorator at the top that wraps the rest, but the user would have to define
    # the "cache key" themselves which seems riskier (As opposed to as below, where it's defined
    # locally that sku and location are the parameters that make a resource unique)
    # This also would prevent fine-grained caching where leaf resources are still created.
    def set_cache(self, enabled, *args):
        self._cache_key = (self.__class__.__name__, *args)
        self._use_cache = enabled

    def create_resource(self, name, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return {}

    def remove_resource(self, name, **kwargs):  # pylint: disable=unused-argument
        pass

    def remove_resource_with_record_override(self, name, **kwargs):
        with self.override_disable_recording():
            self.remove_resource(name, **kwargs)

    @classmethod
    def _perform_pending_deletes(cls):
        _logger.debug("Perform all delayed resource removal.")
        for each_delete in [e for e in cls._cache_pending_deletes.values()]:
            try:
                _logger.debug("Performing delayed delete")
                each_delete()
            except Exception as e: #pylint: disable=broad-except
                # Intentionally broad exception to attempt to leave as few orphan resources as possible even on error.
                _logger.debug("Exception while performing delayed deletes (this can happen): %s", e)

class SingleValueReplacer(RecordingProcessor):
    # pylint: disable=no-member
    def process_request(self, request):
        from six.moves.urllib_parse import quote_plus  # pylint: disable=import-error,import-outside-toplevel
        if self.random_name in request.uri:
            request.uri = request.uri.replace(self.random_name, self.moniker)
        elif quote_plus(self.random_name) in request.uri:
            request.uri = request.uri.replace(quote_plus(self.random_name),
                                              quote_plus(self.moniker))

        if is_text_payload(request) and request.body:
            body = str(request.body, 'utf-8') if isinstance(request.body, bytes) else str(request.body)
            if self.random_name in body:
                request.body = body.replace(self.random_name, self.moniker)

        return request

    def process_response(self, response):
        if is_text_payload(response) and response['body']['string']:
            response['body']['string'] = response['body']['string'].replace(self.random_name,
                                                                            self.moniker)

        self.replace_header(response, 'location', self.random_name, self.moniker)
        self.replace_header(response, 'azure-asyncoperation', self.random_name, self.moniker)

        return response
