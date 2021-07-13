import types

try:
    from collections.abc import Mapping, MutableMapping
except ImportError:
    from collections import Mapping, MutableMapping


# Shamelessly stolen from https://github.com/kennethreitz/requests/blob/master/requests/structures.py
class CaseInsensitiveDict(MutableMapping):
    """
    A case-insensitive ``dict``-like object.
    Implements all methods and operations of
    ``collections.abc.MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.
    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive::
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True
    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.
    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """

    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


def partition_dict(predicate, dictionary):
    true_dict = {}
    false_dict = {}
    for key, value in dictionary.items():
        this_dict = true_dict if predicate(key, value) else false_dict
        this_dict[key] = value
    return true_dict, false_dict


def compose(*functions):
    def composed(incoming):
        res = incoming
        for function in reversed(functions):
            if function:
                res = function(res)
        return res

    return composed


def read_body(request):
    if hasattr(request.body, "read"):
        return request.body.read()
    return request.body


def auto_decorate(decorator, predicate=lambda name, value: isinstance(value, types.FunctionType)):
    def maybe_decorate(attribute, value):
        if predicate(attribute, value):
            value = decorator(value)
        return value

    class DecorateAll(type):
        def __setattr__(cls, attribute, value):
            return super(DecorateAll, cls).__setattr__(attribute, maybe_decorate(attribute, value))

        def __new__(cls, name, bases, attributes_dict):
            new_attributes_dict = {
                attribute: maybe_decorate(attribute, value) for attribute, value in attributes_dict.items()
            }
            return super(DecorateAll, cls).__new__(cls, name, bases, new_attributes_dict)

    return DecorateAll
