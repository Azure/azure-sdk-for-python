import sys
import warnings
import textwrap


msg = textwrap.dedent("""
    You are running Setuptools on Python 2, which is no longer
    supported and
    >>> SETUPTOOLS WILL STOP WORKING <<<
    in a subsequent release (no sooner than 2020-04-20).
    Please ensure you are installing
    Setuptools using pip 9.x or later or pin to `setuptools<45`
    in your environment.
    If you have done those things and are still encountering
    this message, please follow up at
    https://bit.ly/setuptools-py2-warning.
    """)

pre = "Setuptools will stop working on Python 2\n"

sys.version_info < (3,) and warnings.warn(pre + "*" * 60 + msg + "*" * 60)
