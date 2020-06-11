# -*- encoding: utf-8 -*-
# json_delta: a library for computing deltas between JSON-serializable
# structures.
# json_delta/_patch.py
#
# Copyright 2012‒2015 Philip J. Roberts <himself@phil-roberts.name>.
# BSD License applies; see the LICENSE file, or
# http://opensource.org/licenses/BSD-2-Clause
'''Functions for applying JSON-format patches.'''
from __future__ import unicode_literals, print_function
import copy


def patch(struc, diff, in_place=True):
    '''Apply the sequence of diff stanzas ``diff`` to the structure
    ``struc``.

    By default, this function modifies ``struc`` in place; set
    ``in_place`` to ``False`` to return a patched copy of struc
    instead:

    >>> will_change = [16]
    >>> wont_change = [16]
    >>> patch(will_change, [[[0]]])
    []
    >>> will_change
    []
    >>> patch(wont_change, [[[0]]], False)
    []
    >>> wont_change
    [16]
    '''
    if not in_place:
        struc = copy.deepcopy(struc)
    for stanza in diff:
        struc = patch_stanza(struc, stanza)
    return struc


def patch_stanza(struc, stanza):
    '''Applies the stanza ``stanza`` to the structure ``struc`` as
    a patch.

    Note that this function modifies ``struc`` in-place into the
    target of ``stanza``.  If ``struc`` is a :func:`tuple`, you get a
    new tuple with the appropriate modification made:

    >>> patch_stanza((17, 3.141593, None), [[1], 3.14159265])
    (17, 3.14159265, None)

    '''
    changeback = False
    if type(struc) is tuple:
        changeback = True
        struc = list(struc)[:]
    key = stanza[0]
    if not key:
        struc = stanza[1]
        changeback = False
    elif len(key) == 1:
        if len(stanza) == 1:
            del struc[key[0]]
        elif len(stanza) == 3:
            assert stanza[2] == 'i', stanza
            if isinstance(struc, list):
                struc.insert(key[0], stanza[1])
            else:
                assert isinstance(struc, dict)
                struc[key[0]] = stanza[1]
        elif isinstance(struc, list) and key[0] == len(struc):
            struc.append(stanza[1])
        else:
            struc[key[0]] = stanza[1]
    else:
        pass_key = key[:]
        pass_struc_key = pass_key.pop(0)
        pass_struc = struc[pass_struc_key]
        pass_diff = [pass_key] + stanza[1:]
        struc[pass_struc_key] = patch_stanza(pass_struc, pass_diff)
    if changeback:
        struc = tuple(struc)
    return struc
