# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import functools

from .base import ReplayableTest
from .utilities import create_random_name, is_text_payload, trim_kwargs_from_test_function
from .recording_processors import RecordingProcessor


# Core Utility

class AbstractPreparer(object):
    def __init__(self, name_prefix, name_len, disable_recording=False):
        self.name_prefix = name_prefix
        self.name_len = name_len
        self.resource_moniker = None
        self.resource_random_name = None
        self.test_class_instance = None
        self.live_test = False
        self.disable_recording = disable_recording

    def __call__(self, fn):
        def _preparer_wrapper(test_class_instance, **kwargs):
            self.live_test = not isinstance(test_class_instance, ReplayableTest)
            self.test_class_instance = test_class_instance

            if self.live_test or test_class_instance.in_recording:
                resource_name = self.random_name
                if not self.live_test and isinstance(self, RecordingProcessor):
                    test_class_instance.recording_processors.append(self)
            else:
                resource_name = self.moniker

            with self.override_disable_recording():
                parameter_update = self.create_resource(
                    resource_name,
                    **kwargs
                )

            if parameter_update:
                kwargs.update(parameter_update)

            trim_kwargs_from_test_function(fn, kwargs)

            try:
                fn(test_class_instance, **kwargs)
            finally:
                # Russian Doll - the last declared resource to be deleted first.
                self.remove_resource_with_record_override(resource_name, **kwargs)

        setattr(_preparer_wrapper, '__is_preparer', True)
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

    def create_resource(self, name, **kwargs):  # pylint: disable=unused-argument,no-self-use
        return {}

    def remove_resource(self, name, **kwargs):  # pylint: disable=unused-argument
        pass

    def remove_resource_with_record_override(self, name, **kwargs):
        with self.override_disable_recording():
            self.remove_resource(name, **kwargs)


class SingleValueReplacer(RecordingProcessor):
    # pylint: disable=no-member
    def process_request(self, request):
        from six.moves.urllib_parse import quote_plus  # pylint: disable=import-error,relative-import
        if self.random_name in request.uri:
            request.uri = request.uri.replace(self.random_name, self.moniker)
        elif quote_plus(self.random_name) in request.uri:
            request.uri = request.uri.replace(quote_plus(self.random_name),
                                              quote_plus(self.moniker))

        if is_text_payload(request) and request.body:
            body = str(request.body)
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
