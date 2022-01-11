import collections
import copy
import sys
import inspect
import logging

import wrapt

from .compat import contextlib
from .errors import UnhandledHTTPRequestError
from .matchers import requests_match, uri, method, get_matchers_results
from .patch import CassettePatcherBuilder
from .serializers import yamlserializer
from .persisters.filesystem import FilesystemPersister
from .util import partition_dict

try:
    from asyncio import iscoroutinefunction
except ImportError:

    def iscoroutinefunction(*args, **kwargs):
        return False


if sys.version_info[:2] >= (3, 5):
    from ._handle_coroutine import handle_coroutine
else:

    def handle_coroutine(*args, **kwags):
        raise NotImplementedError("Not implemented on Python 2")


log = logging.getLogger(__name__)


class CassetteContextDecorator(object):
    """Context manager/decorator that handles installing the cassette and
    removing cassettes.

    This class defers the creation of a new cassette instance until
    the point at which it is installed by context manager or
    decorator. The fact that a new cassette is used with each
    application prevents the state of any cassette from interfering
    with another.

    Instances of this class are NOT reentrant as context managers.
    However, functions that are decorated by
    ``CassetteContextDecorator`` instances ARE reentrant. See the
    implementation of ``__call__`` on this class for more details.
    There is also a guard against attempts to reenter instances of
    this class as a context manager in ``__exit__``.
    """

    _non_cassette_arguments = ("path_transformer", "func_path_generator")

    @classmethod
    def from_args(cls, cassette_class, **kwargs):
        return cls(cassette_class, lambda: dict(kwargs))

    def __init__(self, cls, args_getter):
        self.cls = cls
        self._args_getter = args_getter
        self.__finish = None

    def _patch_generator(self, cassette):
        with contextlib.ExitStack() as exit_stack:
            for patcher in CassettePatcherBuilder(cassette).build():
                exit_stack.enter_context(patcher)
            log_format = "{action} context for cassette at {path}."
            log.debug(log_format.format(action="Entering", path=cassette._path))
            yield cassette
            log.debug(log_format.format(action="Exiting", path=cassette._path))
            # TODO(@IvanMalison): Hmmm. it kind of feels like this should be
            # somewhere else.
            cassette._save()

    def __enter__(self):
        # This assertion is here to prevent the dangerous behavior
        # that would result from forgetting about a __finish before
        # completing it.
        # How might this condition be met? Here is an example:
        # context_decorator = Cassette.use('whatever')
        # with context_decorator:
        #     with context_decorator:
        #         pass
        assert self.__finish is None, "Cassette already open."
        other_kwargs, cassette_kwargs = partition_dict(
            lambda key, _: key in self._non_cassette_arguments, self._args_getter()
        )
        if other_kwargs.get("path_transformer"):
            transformer = other_kwargs["path_transformer"]
            cassette_kwargs["path"] = transformer(cassette_kwargs["path"])
        self.__finish = self._patch_generator(self.cls.load(**cassette_kwargs))
        return next(self.__finish)

    def __exit__(self, *args):
        next(self.__finish, None)
        self.__finish = None

    @wrapt.decorator
    def __call__(self, function, instance, args, kwargs):
        # This awkward cloning thing is done to ensure that decorated
        # functions are reentrant. This is required for thread
        # safety and the correct operation of recursive functions.
        args_getter = self._build_args_getter_for_decorator(function)
        return type(self)(self.cls, args_getter)._execute_function(function, args, kwargs)

    def _execute_function(self, function, args, kwargs):
        def handle_function(cassette):
            if cassette.inject:
                return function(cassette, *args, **kwargs)
            else:
                return function(*args, **kwargs)

        if iscoroutinefunction(function):
            return handle_coroutine(vcr=self, fn=handle_function)
        if inspect.isgeneratorfunction(function):
            return self._handle_generator(fn=handle_function)

        return self._handle_function(fn=handle_function)

    def _handle_generator(self, fn):
        """Wraps a generator so that we're inside the cassette context for the
        duration of the generator.
        """
        with self as cassette:
            coroutine = fn(cassette)
            # We don't need to catch StopIteration. The caller (Tornado's
            # gen.coroutine, for example) will handle that.
            to_yield = next(coroutine)
            while True:
                try:
                    to_send = yield to_yield
                except Exception:
                    to_yield = coroutine.throw(*sys.exc_info())
                else:
                    try:
                        to_yield = coroutine.send(to_send)
                    except StopIteration:
                        break

    def _handle_function(self, fn):
        with self as cassette:
            return fn(cassette)

    @staticmethod
    def get_function_name(function):
        return function.__name__

    def _build_args_getter_for_decorator(self, function):
        def new_args_getter():
            kwargs = self._args_getter()
            if "path" not in kwargs:
                name_generator = kwargs.get("func_path_generator") or self.get_function_name
                path = name_generator(function)
                kwargs["path"] = path
            return kwargs

        return new_args_getter


class Cassette(object):
    """A container for recorded requests and responses"""

    @classmethod
    def load(cls, **kwargs):
        """Instantiate and load the cassette stored at the specified path."""
        new_cassette = cls(**kwargs)
        new_cassette._load()
        return new_cassette

    @classmethod
    def use_arg_getter(cls, arg_getter):
        return CassetteContextDecorator(cls, arg_getter)

    @classmethod
    def use(cls, **kwargs):
        return CassetteContextDecorator.from_args(cls, **kwargs)

    def __init__(
        self,
        path,
        serializer=None,
        persister=None,
        record_mode="once",
        match_on=(uri, method),
        before_record_request=None,
        before_record_response=None,
        custom_patches=(),
        inject=False,
    ):
        self._persister = persister or FilesystemPersister
        self._path = path
        self._serializer = serializer or yamlserializer
        self._match_on = match_on
        self._before_record_request = before_record_request or (lambda x: x)
        log.info(self._before_record_request)
        self._before_record_response = before_record_response or (lambda x: x)
        self.inject = inject
        self.record_mode = record_mode
        self.custom_patches = custom_patches

        # self.data is the list of (req, resp) tuples
        self.data = []
        self.play_counts = collections.Counter()
        self.dirty = False
        self.rewound = False

    @property
    def play_count(self):
        return sum(self.play_counts.values())

    @property
    def all_played(self):
        """Returns True if all responses have been played, False otherwise."""
        return self.play_count == len(self)

    @property
    def requests(self):
        return [request for (request, response) in self.data]

    @property
    def responses(self):
        return [response for (request, response) in self.data]

    @property
    def write_protected(self):
        return self.rewound and self.record_mode == "once" or self.record_mode == "none"

    def append(self, request, response):
        """Add a request, response pair to this cassette"""
        log.info("Appending request %s and response %s", request, response)
        request = self._before_record_request(request)
        if not request:
            return
        # Deepcopy is here because mutation of `response` will corrupt the
        # real response.
        response = copy.deepcopy(response)
        response = self._before_record_response(response)
        if response is None:
            return
        self.data.append((request, response))
        self.dirty = True

    def filter_request(self, request):
        return self._before_record_request(request)

    def _responses(self, request):
        """
        internal API, returns an iterator with all responses matching
        the request.
        """
        request = self._before_record_request(request)
        for index, (stored_request, response) in enumerate(self.data):
            if requests_match(request, stored_request, self._match_on):
                yield index, response

    def can_play_response_for(self, request):
        request = self._before_record_request(request)
        return request and request in self and self.record_mode != "all" and self.rewound

    def play_response(self, request):
        """
        Get the response corresponding to a request, but only if it
        hasn't been played back before, and mark it as played
        """
        for index, response in self._responses(request):
            if self.play_counts[index] == 0:
                self.play_counts[index] += 1
                return response
        # The cassette doesn't contain the request asked for.
        raise UnhandledHTTPRequestError(
            "The cassette (%r) doesn't contain the request (%r) asked for" % (self._path, request)
        )

    def responses_of(self, request):
        """
        Find the responses corresponding to a request.
        This function isn't actually used by VCR internally, but is
        provided as an external API.
        """
        responses = [response for index, response in self._responses(request)]

        if responses:
            return responses
        # The cassette doesn't contain the request asked for.
        raise UnhandledHTTPRequestError(
            "The cassette (%r) doesn't contain the request (%r) asked for" % (self._path, request)
        )

    def rewind(self):
        self.play_counts = collections.Counter()

    def find_requests_with_most_matches(self, request):
        """
        Get the most similar request(s) stored in the cassette
        of a given request as a list of tuples like this:
        - the request object
        - the successful matchers as string
        - the failed matchers and the related assertion message with the difference details as strings tuple

        This is useful when a request failed to be found,
        we can get the similar request(s) in order to know what have changed in the request parts.
        """
        best_matches = []
        request = self._before_record_request(request)
        for index, (stored_request, response) in enumerate(self.data):
            successes, fails = get_matchers_results(request, stored_request, self._match_on)
            best_matches.append((len(successes), stored_request, successes, fails))
        best_matches.sort(key=lambda t: t[0], reverse=True)
        # Get the first best matches (multiple if equal matches)
        final_best_matches = []

        if not best_matches:
            return final_best_matches

        previous_nb_success = best_matches[0][0]
        for best_match in best_matches:
            nb_success = best_match[0]
            # Do not keep matches that have 0 successes,
            # it means that the request is totally different from
            # the ones stored in the cassette
            if nb_success < 1 or previous_nb_success != nb_success:
                break
            previous_nb_success = nb_success
            final_best_matches.append(best_match[1:])

        return final_best_matches

    def _as_dict(self):
        return {"requests": self.requests, "responses": self.responses}

    def _save(self, force=False):
        if force or self.dirty:
            self._persister.save_cassette(self._path, self._as_dict(), serializer=self._serializer)
            self.dirty = False

    def _load(self):
        try:
            requests, responses = self._persister.load_cassette(self._path, serializer=self._serializer)
            for request, response in zip(requests, responses):
                self.append(request, response)
            self.dirty = False
            self.rewound = True
        except ValueError:
            pass

    def __str__(self):
        return "<Cassette containing {} recorded response(s)>".format(len(self))

    def __len__(self):
        """Return the number of request,response pairs stored in here"""
        return len(self.data)

    def __contains__(self, request):
        """Return whether or not a request has been stored"""
        for index, response in self._responses(request):
            if self.play_counts[index] == 0:
                return True
        return False
