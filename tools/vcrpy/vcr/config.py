import copy

try:
    from collections import abc as collections_abc  # only works on python 3.3+
except ImportError:
    import collections as collections_abc
import functools
import inspect
import os
import types

import six

from .cassette import Cassette
from .serializers import yamlserializer, jsonserializer
from .persisters.filesystem import FilesystemPersister
from .util import compose, auto_decorate
from . import matchers
from . import filters


class VCR(object):
    @staticmethod
    def is_test_method(method_name, function):
        return method_name.startswith("test") and isinstance(function, types.FunctionType)

    @staticmethod
    def ensure_suffix(suffix):
        def ensure(path):
            if not path.endswith(suffix):
                return path + suffix
            return path

        return ensure

    def __init__(
        self,
        path_transformer=None,
        before_record_request=None,
        custom_patches=(),
        filter_query_parameters=(),
        ignore_hosts=(),
        record_mode="once",
        ignore_localhost=False,
        filter_headers=(),
        before_record_response=None,
        filter_post_data_parameters=(),
        match_on=("method", "scheme", "host", "port", "path", "query"),
        before_record=None,
        inject_cassette=False,
        serializer="yaml",
        cassette_library_dir=None,
        func_path_generator=None,
        decode_compressed_response=False,
    ):
        self.serializer = serializer
        self.match_on = match_on
        self.cassette_library_dir = cassette_library_dir
        self.serializers = {"yaml": yamlserializer, "json": jsonserializer}
        self.matchers = {
            "method": matchers.method,
            "uri": matchers.uri,
            "url": matchers.uri,  # matcher for backwards compatibility
            "scheme": matchers.scheme,
            "host": matchers.host,
            "port": matchers.port,
            "path": matchers.path,
            "query": matchers.query,
            "headers": matchers.headers,
            "raw_body": matchers.raw_body,
            "body": matchers.body,
        }
        self.persister = FilesystemPersister
        self.record_mode = record_mode
        self.filter_headers = filter_headers
        self.filter_query_parameters = filter_query_parameters
        self.filter_post_data_parameters = filter_post_data_parameters
        self.before_record_request = before_record_request or before_record
        self.before_record_response = before_record_response
        self.ignore_hosts = ignore_hosts
        self.ignore_localhost = ignore_localhost
        self.inject_cassette = inject_cassette
        self.path_transformer = path_transformer
        self.func_path_generator = func_path_generator
        self.decode_compressed_response = decode_compressed_response
        self._custom_patches = tuple(custom_patches)

    def _get_serializer(self, serializer_name):
        try:
            serializer = self.serializers[serializer_name]
        except KeyError:
            raise KeyError("Serializer {} doesn't exist or isn't registered".format(serializer_name))
        return serializer

    def _get_matchers(self, matcher_names):
        matchers = []
        try:
            for m in matcher_names:
                matchers.append(self.matchers[m])
        except KeyError:
            raise KeyError("Matcher {} doesn't exist or isn't registered".format(m))
        return matchers

    def use_cassette(self, path=None, **kwargs):
        if path is not None and not isinstance(path, six.string_types):
            function = path
            # Assume this is an attempt to decorate a function
            return self._use_cassette(**kwargs)(function)
        return self._use_cassette(path=path, **kwargs)

    def _use_cassette(self, with_current_defaults=False, **kwargs):
        if with_current_defaults:
            config = self.get_merged_config(**kwargs)
            return Cassette.use(**config)
        # This is made a function that evaluates every time a cassette
        # is made so that changes that are made to this VCR instance
        # that occur AFTER the `use_cassette` decorator is applied
        # still affect subsequent calls to the decorated function.
        args_getter = functools.partial(self.get_merged_config, **kwargs)
        return Cassette.use_arg_getter(args_getter)

    def get_merged_config(self, **kwargs):
        serializer_name = kwargs.get("serializer", self.serializer)
        matcher_names = kwargs.get("match_on", self.match_on)
        path_transformer = kwargs.get("path_transformer", self.path_transformer)
        func_path_generator = kwargs.get("func_path_generator", self.func_path_generator)
        cassette_library_dir = kwargs.get("cassette_library_dir", self.cassette_library_dir)
        additional_matchers = kwargs.get("additional_matchers", ())

        if cassette_library_dir:

            def add_cassette_library_dir(path):
                if not path.startswith(cassette_library_dir):
                    return os.path.join(cassette_library_dir, path)
                return path

            path_transformer = compose(add_cassette_library_dir, path_transformer)
        elif not func_path_generator:
            # If we don't have a library dir, use the functions
            # location to build a full path for cassettes.
            func_path_generator = self._build_path_from_func_using_module

        merged_config = {
            "serializer": self._get_serializer(serializer_name),
            "persister": self.persister,
            "match_on": self._get_matchers(tuple(matcher_names) + tuple(additional_matchers)),
            "record_mode": kwargs.get("record_mode", self.record_mode),
            "before_record_request": self._build_before_record_request(kwargs),
            "before_record_response": self._build_before_record_response(kwargs),
            "custom_patches": self._custom_patches + kwargs.get("custom_patches", ()),
            "inject": kwargs.get("inject_cassette", self.inject_cassette),
            "path_transformer": path_transformer,
            "func_path_generator": func_path_generator,
        }
        path = kwargs.get("path")
        if path:
            merged_config["path"] = path
        return merged_config

    def _build_before_record_response(self, options):
        before_record_response = options.get("before_record_response", self.before_record_response)
        decode_compressed_response = options.get(
            "decode_compressed_response", self.decode_compressed_response
        )
        filter_functions = []
        if decode_compressed_response:
            filter_functions.append(filters.decode_response)
        if before_record_response:
            if not isinstance(before_record_response, collections_abc.Iterable):
                before_record_response = (before_record_response,)
            filter_functions.extend(before_record_response)

        def before_record_response(response):
            for function in filter_functions:
                if response is None:
                    break
                response = function(response)
            return response

        return before_record_response

    def _build_before_record_request(self, options):
        filter_functions = []
        filter_headers = options.get("filter_headers", self.filter_headers)
        filter_query_parameters = options.get("filter_query_parameters", self.filter_query_parameters)
        filter_post_data_parameters = options.get(
            "filter_post_data_parameters", self.filter_post_data_parameters
        )
        before_record_request = options.get(
            "before_record_request", options.get("before_record", self.before_record_request)
        )
        ignore_hosts = options.get("ignore_hosts", self.ignore_hosts)
        ignore_localhost = options.get("ignore_localhost", self.ignore_localhost)
        if filter_headers:
            replacements = [h if isinstance(h, tuple) else (h, None) for h in filter_headers]
            filter_functions.append(functools.partial(filters.replace_headers, replacements=replacements))
        if filter_query_parameters:
            replacements = [p if isinstance(p, tuple) else (p, None) for p in filter_query_parameters]
            filter_functions.append(
                functools.partial(filters.replace_query_parameters, replacements=replacements)
            )
        if filter_post_data_parameters:
            replacements = [p if isinstance(p, tuple) else (p, None) for p in filter_post_data_parameters]
            filter_functions.append(
                functools.partial(filters.replace_post_data_parameters, replacements=replacements)
            )

        hosts_to_ignore = set(ignore_hosts)
        if ignore_localhost:
            hosts_to_ignore.update(("localhost", "0.0.0.0", "127.0.0.1"))
        if hosts_to_ignore:
            filter_functions.append(self._build_ignore_hosts(hosts_to_ignore))

        if before_record_request:
            if not isinstance(before_record_request, collections_abc.Iterable):
                before_record_request = (before_record_request,)
            filter_functions.extend(before_record_request)

        def before_record_request(request):
            request = copy.copy(request)
            for function in filter_functions:
                if request is None:
                    break
                request = function(request)
            return request

        return before_record_request

    @staticmethod
    def _build_ignore_hosts(hosts_to_ignore):
        def filter_ignored_hosts(request):
            if hasattr(request, "host") and request.host in hosts_to_ignore:
                return
            return request

        return filter_ignored_hosts

    @staticmethod
    def _build_path_from_func_using_module(function):
        return os.path.join(os.path.dirname(inspect.getfile(function)), function.__name__)

    def register_serializer(self, name, serializer):
        self.serializers[name] = serializer

    def register_matcher(self, name, matcher):
        self.matchers[name] = matcher

    def register_persister(self, persister):
        # Singleton, no name required
        self.persister = persister

    def test_case(self, predicate=None):
        predicate = predicate or self.is_test_method
        return six.with_metaclass(auto_decorate(self.use_cassette, predicate))
