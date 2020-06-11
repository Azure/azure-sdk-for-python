#! /usr/bin/env python
#
# Public domain
# Idea from Georg Brandl. Foolishly implemented by Michael Foord and Richard
# Jones
# E-mail: richard AT mechanicalcat DOT net
u"""Evaluate and display command line expressions with ``python -me expr``.

For example::

    $ python -me 1 + 1
    2

Like python -c but no need for a print. But wait, there's more.

As a bonus, if the first argument is a module name then it will output the
location of the module source code::

    $ python -me os
    /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/os.py

If you follow the name of the module with a command then the module will be
opened with that command. For example, the following will open the os module
source in vim::

    $ python -me os vim

The "e" module recognises the special command names "edit" and "view" which
will result in it looking up your editor and viewer commands in the
environment variables $EDITOR and $PAGER respectively. The latter defaults to
"less". This is slightly easier than writing, for example::

    $ vim `python -me os`

... especially if you're going back to edit a previous "python -me" command
using line editing.

Also, "python -me help" is a shortcut to Python's interactive help mechanism.

Idea from Georg Brandl. Foolishly implemented by Michael Foord and Richard
Jones.
"""

import os
import sys
import subprocess


def execute(arg):
    exec (compile(arg, '<cmdline>', 'single'))


def locate(arg):
    try:
        __import__(arg)
    except ImportError:
        return None

    try:
        mod = sys.modules[arg]
    except KeyError:
        print ('%s is not a valid module name' % arg)
        sys.exit(1)

    location = getattr(mod, '__file__', 'None')
    if location.endswith('.pyc'):
        location = location[:-1]
    return location


def main(args):
    if not args or args[0] in ('-h', '--help'):
        print (__doc__)
        return

    if args[0] == 'help':
        help()

    fn = locate(args[0])
    if fn is None:
        # right, just try to execute the stuff we're
        execute(' '.join(args))
        return

    if len(args) == 1:
        print (fn)
        return

    if not fn.endswith('.py'):
        sys.exit('Module (%s) is not Python' % fn)

    prog = args[1]
    if prog == 'edit':
        prog = os.environ['EDITOR']
    elif prog == 'view':
        prog = os.environ.get('PAGER', 'less')
    sys.exit(subprocess.call(' '.join([prog, fn]), shell=True))


if __name__ == '__main__':
    main(sys.argv[1:])
