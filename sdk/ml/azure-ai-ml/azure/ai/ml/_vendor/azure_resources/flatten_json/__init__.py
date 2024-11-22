#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import copy
import json
import re
import sys
from math import isnan


try:
    # 3.8 and up
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


def check_if_numbers_are_consecutive(list_):
    """
    Returns True if numbers in the list are consecutive

    :param list_: list of integers
    :return: Boolean
    """
    return all(True if second - first == 1 else False for first, second in zip(list_[:-1], list_[1:]))


def _construct_key(previous_key, separator, new_key, replace_separators=None):
    """
    Returns the new_key if no previous key exists, otherwise concatenates
    previous key, separator, and new_key
    :param previous_key:
    :param separator:
    :param new_key:
    :param str replace_separators: Replace separators within keys
    :return: a string if previous_key exists and simply passes through the
    new_key otherwise
    """
    if replace_separators is not None:
        new_key = str(new_key).replace(separator, replace_separators)
    if previous_key:
        return "{}{}{}".format(previous_key, separator, new_key)
    else:
        return new_key


def flatten(nested_dict, separator="_", root_keys_to_ignore=None, replace_separators=None):
    """
    Flattens a dictionary with nested structure to a dictionary with no
    hierarchy
    Consider ignoring keys that you are not interested in to prevent
    unnecessary processing
    This is specially true for very deep objects

    :param nested_dict: dictionary we want to flatten
    :param separator: string to separate dictionary keys by
    :param root_keys_to_ignore: set of root keys to ignore from flattening
    :param str replace_separators: Replace separators within keys
    :return: flattened dictionary
    """
    assert isinstance(nested_dict, dict), "flatten requires a dictionary input"
    assert isinstance(separator, str), "separator must be string"

    if root_keys_to_ignore is None:
        root_keys_to_ignore = set()

    if len(nested_dict) == 0:
        return {}

    # This global dictionary stores the flattened keys and values and is
    # ultimately returned
    flattened_dict = dict()

    def _flatten(object_, key):
        """
        For dict, list and set objects_ calls itself on the elements and for
        other types assigns the object_ to
        the corresponding key in the global flattened_dict
        :param object_: object to flatten
        :param key: carries the concatenated key for the object_
        :return: None
        """
        # Empty object can't be iterated, take as is
        if not object_:
            flattened_dict[key] = object_
        # These object types support iteration
        elif isinstance(object_, dict):
            for object_key in object_:
                if not (not key and object_key in root_keys_to_ignore):
                    _flatten(
                        object_[object_key],
                        _construct_key(key, separator, object_key, replace_separators=replace_separators),
                    )
        elif isinstance(object_, (list, set, tuple)):
            for index, item in enumerate(object_):
                _flatten(item, _construct_key(key, separator, index, replace_separators=replace_separators))
        # Anything left take as is
        else:
            flattened_dict[key] = object_

    _flatten(nested_dict, None)
    return flattened_dict


flatten_json = flatten


def flatten_preserve_lists(
    nested_dict, separator="_", root_keys_to_ignore=None, max_list_index=3, max_depth=3, replace_separators=None
):
    """
    Flattens a dictionary with nested structure to a dictionary with no
    hierarchy
    Consider ignoring keys that you are not interested in to prevent
    unnecessary processing
    This is specially true for very deep objects
    This preserves list structure, and
    you can specify max_list_index and max_depth to limit processing

    Child elements with only one value inside
    will be unwrapped and become parent's value.

    :param nested_dict: dictionary we want to flatten
    :param separator: string to separate dictionary keys by
    :param root_keys_to_ignore: set of root keys to ignore from flattening
    :param max_list_index: maximum list index to process
    :param max_depth: maximum nesting depth to process
    :param str replace_separators: Replace separators within keys
    :return: flattened dictionary
    """

    assert isinstance(nested_dict, dict), "flatten requires a dictionary input"
    assert isinstance(separator, str), "separator must be a string"

    if root_keys_to_ignore is None:
        root_keys_to_ignore = set()

    # This global dictionary stores the flattened keys and values and is
    # ultimately returned
    flattened_dict = dict()

    def _flatten(object_, key):
        """
        For dict, list and set objects_ calls itself on the elements and for
        other types assigns the object_ to
        the corresponding key in the global flattened_dict
        :param object_: object to flatten
        :param key: carries the concatenated key for the object_
        :return: None
        """

        # Empty object can't be iterated, take as is
        if not object_:
            flattened_dict[key] = object_

        # These object types support iteration
        # dict always go into columns
        elif isinstance(object_, dict):
            first_key = list(object_.keys())[0]
            # if only 1 child value, and child value not a dict or list
            # flatten immediately
            is_iter = isinstance(object_[first_key], Iterable)
            if len(object_) == 1 and not is_iter:
                flattened_dict[key] = object_[first_key]
            else:
                for object_key in object_:
                    if not (not key and object_key in root_keys_to_ignore):
                        _flatten(
                            object_[object_key],
                            _construct_key(key, separator, object_key, replace_separators=replace_separators),
                        )

        elif isinstance(object_, (list, set, tuple)):
            for index, item in enumerate(object_):
                key = _construct_key(key, separator, index, replace_separators=replace_separators)
                _flatten(item, key)

        else:
            flattened_dict[key] = object_

    def _flatten_low_entropy(object_, key, cur_depth, max_depth_inner):
        """
        For dict, list and set objects_ calls itself on the elements and for
        other types assigns the object_ to
        the corresponding key in the global flattened_dict

        :param object_: object to flatten
        :param key: carries the concatenated key for the object_
        :return: None
        """
        cur_depth = cur_depth + 1  # increase current_depth
        debug = 0

        # write latest child as value if max_depth exceeded
        if cur_depth > max_depth_inner:
            global_max_record = int(max(list(list_prebuilt_flattened_dict.keys())))
            for d in list_prebuilt_flattened_dict[str(global_max_record)]:
                d[key] = object_

        else:
            # Empty object can't be iterated, take as is
            if not object_:
                global_max_record = int(max(list(list_prebuilt_flattened_dict.keys())))
                for d in list_prebuilt_flattened_dict[str(global_max_record)]:
                    d[key] = object_

            # These object types support iteration
            # dict always go into columns
            elif isinstance(object_, dict):
                first_key = list(object_.keys())[0]
                # if only 1 child value, and child value
                # not a dict or list, flatten immediately
                if len(object_) == 1 and not (
                    isinstance(object_[first_key], dict) or isinstance(object_[first_key], list)
                ):
                    global_max_record = int(max(list(list_prebuilt_flattened_dict.keys())))

                    for d in list_prebuilt_flattened_dict[str(global_max_record)]:
                        d[key] = object_[first_key]

                else:
                    for object_key, val in sorted(
                        object_.items(), key=lambda x: (str(type(x[1])), len(str(x[1]))), reverse=False
                    ):
                        if not (not key and object_key in root_keys_to_ignore):
                            _flatten_low_entropy(
                                object_[object_key],
                                _construct_key(key, separator, object_key, replace_separators=replace_separators),
                                cur_depth,
                                max_depth_inner,
                            )

            # lists could go into rows, like in a relational database
            elif isinstance(object_, list) or isinstance(object_, set):
                if debug:
                    print("\nparent key of list:", key, "| length: ", str(len(object_)))

                # need to remember global list state when we entered
                # this recursion
                global_max_record_start = int(max(list(list_prebuilt_flattened_dict.keys())))
                entry = copy.deepcopy(list_prebuilt_flattened_dict[str(global_max_record_start)])

                for index, item in enumerate(object_):
                    if debug:
                        print("  list key:", key, " index: " + str(index), "vals: ", item)

                    sub = -1
                    if isinstance(item, dict):
                        first_value = list(item.values())[0]
                        if isinstance(first_value, float):
                            sub = first_value

                    if not isnan(sub) and index < max_list_index:
                        # start from second element, 1st element is like column
                        if index > 0:
                            global_max_record = int(max(list(list_prebuilt_flattened_dict.keys())))

                            list_prebuilt_flattened_dict[str(global_max_record + 1)] = copy.deepcopy(entry)

                        _flatten_low_entropy(item, key, cur_depth, max_depth_inner)
                    else:
                        pass

                list_prebuilt_flattened_dict["0"] = [
                    subel for k, v in sorted(list_prebuilt_flattened_dict.items()) for idx, subel in enumerate(v)
                ]

                for key in list(sorted(list_prebuilt_flattened_dict.keys())):
                    if key != "0":
                        del list_prebuilt_flattened_dict[key]
                if debug:
                    print("collapsed global list")

            # Anything left take as is, assuming you hit the end of the line.
            else:
                # in this case, there may be
                # a list of prebuilt_flattened_dict by now
                # so need to update them all.
                global_max_record = int(max(list(list_prebuilt_flattened_dict.keys())))

                for d in list_prebuilt_flattened_dict[str(global_max_record)]:
                    d[key] = object_

                    # decrease depth counter
        cur_depth -= 1

    _flatten(nested_dict, None)

    # get unique column names, without the integers
    # TODO: potential issue: what if column names have digits naturally?
    reskeys = list(flattened_dict.keys())
    unique_integers = list(set([separator + char for key in reskeys for char in key if char.isdigit()]))
    regex = "|".join(unique_integers)
    regex += "|" + regex.replace(".", "")
    unique_columns = list(set([re.sub("(" + regex + ")", "", key) for key in reskeys]))

    # create global dict, now with unique column names
    prebuilt_flattened_dict = {column: None for column in unique_columns}

    # initialize global record list
    list_prebuilt_flattened_dict = {"0": [prebuilt_flattened_dict]}

    _flatten_low_entropy(nested_dict, None, cur_depth=0, max_depth_inner=max_depth)

    return list_prebuilt_flattened_dict["0"]


def _unflatten_asserts(flat_dict, separator):
    assert isinstance(flat_dict, dict), "un_flatten requires dictionary input"
    assert isinstance(separator, str), "separator must be string"
    assert all(
        (not value or not isinstance(value, Iterable) or isinstance(value, str) for value in flat_dict.values())
    ), "provided dict is not flat"


def unflatten(flat_dict, separator="_"):
    """
    Creates a hierarchical dictionary from a flattened dictionary
    Assumes no lists are present
    :param flat_dict: a dictionary with no hierarchy
    :param separator: a string that separates keys
    :return: a dictionary with hierarchy
    """
    _unflatten_asserts(flat_dict, separator)

    # This global dictionary is mutated and returned
    unflattened_dict = dict()

    def _unflatten(dic, keys, value):
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})

        dic[keys[-1]] = value

    list_keys = sorted(flat_dict.keys())
    for i, item in enumerate(list_keys):
        if i != len(list_keys) - 1:
            split_key = item.split(separator)
            next_split_key = list_keys[i + 1].split(separator)
            if not split_key == next_split_key[:-1]:
                _unflatten(unflattened_dict, item.split(separator), flat_dict[item])
            else:
                pass  # if key contained in next key, json will be invalid.
        else:
            #  last element
            _unflatten(unflattened_dict, item.split(separator), flat_dict[item])
    return unflattened_dict


def unflatten_list(flat_dict, separator="_"):
    """
    Unflattens a dictionary, first assuming no lists exist and then tries to
    identify lists and replaces them
    This is probably not very efficient and has not been tested extensively
    Feel free to add test cases or rewrite the logic
    Issues that stand out to me:
    - Sorting all the keys in the dictionary, which specially for the root
    dictionary can be a lot of keys
    - Checking that numbers are consecutive is O(N) in number of keys

    :param flat_dict: dictionary with no hierarchy
    :param separator: a string that separates keys
    :return: a dictionary with hierarchy
    """
    _unflatten_asserts(flat_dict, separator)

    # First unflatten the dictionary assuming no lists exist
    unflattened_dict = unflatten(flat_dict, separator)

    def _convert_dict_to_list(object_, parent_object, parent_object_key):
        if isinstance(object_, dict):
            for key in object_:
                if isinstance(object_[key], dict):
                    _convert_dict_to_list(object_[key], object_, key)
            try:
                keys = [int(key) for key in object_]
                keys.sort()
            except (ValueError, TypeError):
                keys = []
            keys_len = len(keys)

            if (
                keys_len > 0
                and sum(keys) == int(((keys_len - 1) * keys_len) / 2)
                and keys[0] == 0
                and keys[-1] == keys_len - 1
                and check_if_numbers_are_consecutive(keys)
            ):
                # The dictionary looks like a list so we're going to replace it
                parent_object[parent_object_key] = []
                for key_index, key in enumerate(keys):
                    parent_object[parent_object_key].append(object_[str(key)])
                    # The list item we just added might be a list itself
                    # https://github.com/amirziai/flatten/issues/15
                    _convert_dict_to_list(
                        parent_object[parent_object_key][-1], parent_object[parent_object_key], key_index
                    )

    _convert_dict_to_list(unflattened_dict, None, None)
    return unflattened_dict


def cli(input_stream=sys.stdin, output_stream=sys.stdout):
    raw = input_stream.read()
    input_json = json.loads(raw)
    output = json.dumps(flatten(input_json))
    output_stream.write("{}\n".format(output))
    output_stream.flush()


if __name__ == "__main__":
    cli()
