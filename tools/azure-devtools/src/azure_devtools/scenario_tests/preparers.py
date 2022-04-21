# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import functools
import logging
from collections import namedtuple
from threading import Lock

from .base import ReplayableTest
from .utilities import create_random_name, is_text_payload, trim_kwargs_from_test_function
from .recording_processors import RecordingProcessor
from .exceptions import AzureNameError

_logger = logging.getLogger(__name__)
# Core Utility


class AbstractPreparer(object):
    _cache_lock = Lock()
    _resource_cache = {}
    ResourceCacheEntry = namedtuple("ResourceCacheEntry", "resource_name kwargs preparer")

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

    def _prepare_create_resource(self, test_class_instance, **kwargs):
        self.live_test = not isinstance(test_class_instance, ReplayableTest)
        self.test_class_instance = test_class_instance

        # This latter conditional is to triage a specific failure mode:
        # If the first cached test run does not have any http traffic, a recording will not have been
        # generated, so in_recording will be True even if live_test is false, so a random name would be given.
        # In cached mode we need to avoid this because then for tests with recordings, they would not have a moniker.
        if (self.live_test or test_class_instance.in_recording) and not (
            not test_class_instance.is_live and test_class_instance.in_recording and self._use_cache
        ):
            resource_name = self.random_name
            if not self.live_test and isinstance(self, RecordingProcessor):
                test_class_instance.recording_processors.append(self)
        else:
            resource_name = self.moniker

        _logger.debug("Creating resource %s for %s", resource_name, self.__class__.__name__)
        with self.override_disable_recording():
            retries = 4
            for i in range(retries):
                try:
                    parameter_update = self.create_resource(resource_name, **kwargs)
                    _logger.debug("Successfully created resource %s", resource_name)
                    break
                except AzureNameError:
                    if i == retries - 1:
                        raise
                    self.resource_random_name = None
                    resource_name = self.random_name
                except Exception as e:
                    msg = "Preparer failure when creating resource {} for test {}: {}".format(
                        self.__class__.__name__, test_class_instance, e
                    )
                    while e:
                        try:
                            e = e.inner_exception
                        except AttributeError:
                            break
                    try:
                        msg += "\nDetailed error message: " + str(e.additional_properties["error"]["message"])
                    except (AttributeError, KeyError):
                        pass

                    _logger.error(msg)
                    raise Exception(msg)

        if parameter_update:
            kwargs.update(parameter_update)

        return resource_name, kwargs

    def __call__(self, fn):
        def _preparer_wrapper(test_class_instance, **kwargs):
            _logger.debug(
                "Entering preparer wrapper for %s and test %s", self.__class__.__name__, str(test_class_instance)
            )

            # If a child is cached we must use the same cached resource their equivalent parent did so all the deps line up
            child_is_cached = getattr(fn, "__use_cache", False)
            # Note: If it is ever desired to make caching inferred, remove this if/throw.
            # This ensures that a user must _very specifically say they want caching_ on an item and all parents.
            if not self._use_cache and child_is_cached:
                raise Exception(
                    """Preparer exception for test {}:\n Child preparers are cached, but parent {} is not.
You must specify use_cache=True in the preparer decorator""".format(
                        test_class_instance, self.__class__.__name__
                    )
                )
            self._use_cache |= child_is_cached
            _logger.debug("Child cache status for %s: %s", self.__class__.__name__, child_is_cached)

            # We must use a cache_key that includes our parents, so that we get a cached stack
            # matching the desired resource stack. (e.g. if parent resource has specific settings)
            try:
                aggregate_cache_key = (self._cache_key, kwargs["__aggregate_cache_key"])
            except KeyError:  # If we're at the root of the cache stack, start with our own key.
                aggregate_cache_key = self._cache_key
            kwargs["__aggregate_cache_key"] = aggregate_cache_key
            self._aggregate_cache_key = aggregate_cache_key
            _logger.debug("Aggregate cache key: %s", aggregate_cache_key)

            # If cache is enabled, and the cached resource exists, use it, otherwise create and store.
            if self._use_cache and aggregate_cache_key in AbstractPreparer._resource_cache:
                _logger.debug("Using cached resource for %s", self.__class__.__name__)
                with self._cache_lock:
                    resource_name, kwargs, _ = AbstractPreparer._resource_cache[aggregate_cache_key]
            else:
                resource_name, kwargs = self._prepare_create_resource(test_class_instance, **kwargs)

            if self._use_cache:
                with self._cache_lock:
                    if aggregate_cache_key not in AbstractPreparer._resource_cache:
                        _logger.debug("Storing cached resource for %s", self.__class__.__name__)
                        AbstractPreparer._resource_cache[aggregate_cache_key] = AbstractPreparer.ResourceCacheEntry(
                            resource_name, kwargs, self
                        )

            if test_class_instance.is_live:
                # Adding this for new proxy testcase
                if hasattr(test_class_instance, "scrubber"):
                    test_class_instance.scrubber.register_name_pair(resource_name, self.moniker)
                else:
                    _logger.info(
                        "This test class instance has no scrubber, so the AbstractPreparer will not scrub any values "
                        "in recordings."
                    )

            # We shouldn't trim the same kwargs that we use for deletion,
            # we may remove some of the variables we needed to do the delete.
            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            trim_kwargs_from_test_function(fn, trimmed_kwargs)

            try:
                try:
                    import asyncio
                except ImportError:
                    fn(test_class_instance, **trimmed_kwargs)
                else:
                    if asyncio.iscoroutinefunction(fn):
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(fn(test_class_instance, **trimmed_kwargs))
                    else:
                        fn(test_class_instance, **trimmed_kwargs)
            finally:
                # If we use cache we delay deletion for the end.
                # This won't guarantee deletion order, but it will guarantee everything delayed
                # does get deleted, in the worst case by getting rid of the RG at the top.
                if not (self._use_cache or child_is_cached):
                    # Russian Doll - the last declared resource to be deleted first.
                    self.remove_resource_with_record_override(resource_name, **kwargs)

        # _logger.debug("Setting up preparer stack for {}".format(self.__class__.__name__))
        setattr(_preparer_wrapper, "__is_preparer", True)
        # Inform the next step in the chain (our parent) that we're cached.
        if self._use_cache or getattr(fn, "__use_cache", False):
            setattr(_preparer_wrapper, "__use_cache", True)
        functools.update_wrapper(_preparer_wrapper, fn)
        return _preparer_wrapper

    @contextlib.contextmanager
    def override_disable_recording(self):
        if hasattr(self.test_class_instance, "disable_recording"):
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
            self.resource_moniker = "{}{:06}".format(self.name_prefix, self.test_class_instance.test_resources_count)
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
        # can't use *args expansion directly into a tuple, py27 compat.
        self._cache_key = tuple([self.__class__.__name__] + list(args))
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
        for resource_name, kwargs, preparer in reversed([e for e in cls._resource_cache.values()]):
            try:
                _logger.debug("Performing delayed delete for: %s %s", preparer, resource_name)
                preparer.remove_resource_with_record_override(resource_name, **kwargs)
            except Exception as e:  # pylint: disable=broad-except
                # Intentionally broad exception to attempt to leave as few orphan resources as possible even on error.
                _logger.warning("Exception while performing delayed deletes (this can happen): %s", e)


class SingleValueReplacer(RecordingProcessor):
    # pylint: disable=no-member
    def process_request(self, request):
        from six.moves.urllib_parse import quote_plus  # pylint: disable=import-error,import-outside-toplevel

        if self.random_name in request.uri:
            request.uri = request.uri.replace(self.random_name, self.moniker)
        elif quote_plus(self.random_name) in request.uri:
            request.uri = request.uri.replace(quote_plus(self.random_name), quote_plus(self.moniker))

        if is_text_payload(request) and request.body:
            body = str(request.body, "utf-8") if isinstance(request.body, bytes) else str(request.body)
            if self.random_name in body:
                request.body = body.replace(self.random_name, self.moniker)

        return request

    def process_response(self, response):
        if is_text_payload(response) and response["body"]["string"]:
            response["body"]["string"] = response["body"]["string"].replace(self.random_name, self.moniker)

        self.replace_header(response, "location", self.random_name, self.moniker)
        self.replace_header(response, "azure-asyncoperation", self.random_name, self.moniker)

        return response
