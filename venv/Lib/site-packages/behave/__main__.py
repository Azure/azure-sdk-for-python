# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import codecs
import sys
import six
from behave import __version__
from behave.configuration import Configuration, ConfigError
from behave.parser import ParserError
from behave.runner import Runner
from behave.runner_util import print_undefined_step_snippets, reset_runtime, \
    InvalidFileLocationError, InvalidFilenameError, FileNotFoundError
from behave.textutil import compute_words_maxsize, text as _text


TAG_HELP = """
Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag::

    --tags @dev

You may even leave off the "@" - behave doesn't mind.

When a tag in a tag expression starts with a ~, this represents boolean NOT::

    --tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR::

    --tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
"(@foo or not @bar) and @zap"::

    --tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND::

    --tags ~@fixme --tags ~@buggy.
""".strip()

# TODO
# Positive tags can be given a threshold to limit the number of occurrences.
# Which can be practical if you are practicing Kanban or CONWIP. This will fail
# if there are more than 3 occurrences of the @qa tag:
#
# --tags @qa:3
# """.strip()


def run_behave(config, runner_class=None):
    """Run behave with configuration.

    :param config:          Configuration object for behave.
    :param runner_class:    Runner class to use or none (use Runner class).
    :return:    0, if successful. Non-zero on failure.

    .. note:: BEST EFFORT, not intended for multi-threaded usage.
    """
    # pylint: disable=too-many-branches, too-many-statements, too-many-return-statements
    if runner_class is None:
        runner_class = Runner

    if config.version:
        print("behave " + __version__)
        return 0

    if config.tags_help:
        print(TAG_HELP)
        return 0

    if config.lang_list:
        from behave.i18n import languages
        stdout = sys.stdout
        if six.PY2:
            # -- PYTHON2: Overcome implicit encode problems (encoding=ASCII).
            stdout = codecs.getwriter("UTF-8")(sys.stdout)
        iso_codes = languages.keys()
        print("Languages available:")
        for iso_code in sorted(iso_codes):
            native = languages[iso_code]["native"][0]
            name = languages[iso_code]["name"][0]
            print(u"%s: %s / %s" % (iso_code, native, name), file=stdout)
        return 0

    if config.lang_help:
        from behave.i18n import languages
        if config.lang_help not in languages:
            print("%s is not a recognised language: try --lang-list" % \
                    config.lang_help)
            return 1
        trans = languages[config.lang_help]
        print(u"Translations for %s / %s" % (trans["name"][0],
                                             trans["native"][0]))
        for kw in trans:
            if kw in "name native".split():
                continue
            print(u"%16s: %s" % (kw.title().replace("_", " "),
                                 u", ".join(w for w in trans[kw] if w != "*")))
        return 0

    if not config.format:
        config.format = [config.default_format]
    elif config.format and "format" in config.defaults:
        # -- CASE: Formatter are specified in behave configuration file.
        #    Check if formatter are provided on command-line, too.
        if len(config.format) == len(config.defaults["format"]):
            # -- NO FORMATTER on command-line: Add default formatter.
            config.format.append(config.default_format)
    if "help" in config.format:
        print_formatters("Available formatters:")
        return 0

    if len(config.outputs) > len(config.format):
        print("CONFIG-ERROR: More outfiles (%d) than formatters (%d)." % \
              (len(config.outputs), len(config.format)))
        return 1

    # -- MAIN PART:
    failed = True
    try:
        reset_runtime()
        runner = runner_class(config)
        failed = runner.run()
    except ParserError as e:
        print(u"ParserError: %s" % e)
    except ConfigError as e:
        print(u"ConfigError: %s" % e)
    except FileNotFoundError as e:
        print(u"FileNotFoundError: %s" % e)
    except InvalidFileLocationError as e:
        print(u"InvalidFileLocationError: %s" % e)
    except InvalidFilenameError as e:
        print(u"InvalidFilenameError: %s" % e)
    except Exception as e:
        # -- DIAGNOSTICS:
        text = _text(e)
        print(u"Exception %s: %s" % (e.__class__.__name__, text))
        raise

    if config.show_snippets and runner.undefined_steps:
        print_undefined_step_snippets(runner.undefined_steps,
                                      colored=config.color)

    return_code = 0
    if failed:
        return_code = 1
    return return_code

def print_formatters(title=None, stream=None):
    """Prints the list of available formatters and their description.

    :param title:   Optional title (as string).
    :param stream:  Optional, output stream to use (default: sys.stdout).
    """
    from behave.formatter._registry  import format_items
    from operator import itemgetter

    if stream is None:
        stream = sys.stdout
    if title:
        stream.write(u"%s\n" % title)

    format_items = sorted(format_items(resolved=True), key=itemgetter(0))
    format_names = [item[0]  for item in format_items]
    column_size = compute_words_maxsize(format_names)
    schema = u"  %-"+ _text(column_size) +"s  %s\n"
    for name, formatter_class in format_items:
        formatter_description = getattr(formatter_class, "description", "")
        stream.write(schema % (name, formatter_description))


def main(args=None):
    """Main function to run behave (as program).

    :param args:    Command-line args (or string) to use.
    :return: 0, if successful. Non-zero, in case of errors/failures.
    """
    config = Configuration(args)
    return run_behave(config)

if __name__ == "__main__":
    # -- EXAMPLE: main("--version")
    sys.exit(main())
