json-delta v1.1.3: A diff/patch pair and library for JSON data
structures. (http://json_delta.readthedocs.org/)

JSON-delta is a multi-language software suite for computing deltas
between JSON-serialized data structures, and applying those deltas as
patches.  It enables separate programs at either end of a
communications channel (e.g. client and server over HTTP, or two
processes talking to one another using bidirectional IPC) to
manipulate a data structure while minimizing communications overhead.

This is the python implementation.  It requires Python version 2.7 or
newer (including Python 3).  It can be installed in the standard way:

$ python setup.py install

(potentially needing superuser privileges).  This will install a
single module named json_delta, and scripts named json_diff,
json_patch and json_cat.

HTML documentation for all four of these can be found in the doc/
directory, along with manpages for the scripts.

Donations to support the continuing development of JSON-delta will be
gratefully received via gratipay (https://gratipay.com/phijaro),
PayPal (himself@phil-roberts.name) or
Bitcoin: (`1HPJHRpVSm1Y4zrgppd2c6LysjxeabbQN4
<bitcoin:1HPJHRpVSm1Y4zrgppd2c6LysjxeabbQN4>`_).



