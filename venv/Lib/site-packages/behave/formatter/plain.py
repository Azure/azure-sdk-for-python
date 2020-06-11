# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.formatter.base import Formatter
from behave.model_describe import ModelPrinter
from behave.textutil import make_indentation


# -----------------------------------------------------------------------------
# CLASS: PlainFormatter
# -----------------------------------------------------------------------------
class PlainFormatter(Formatter):
    """
    Provides a simple plain formatter without coloring/formatting.
    The formatter displays now also:

       * multi-line text (doc-strings)
       * table
       * tags (maybe)
    """
    name = "plain"
    description = "Very basic formatter with maximum compatibility"

    SHOW_MULTI_LINE = True
    SHOW_TAGS = False
    SHOW_ALIGNED_KEYWORDS = False
    DEFAULT_INDENT_SIZE = 2
    RAISE_OUTPUT_ERRORS = True

    def __init__(self, stream_opener, config, **kwargs):
        super(PlainFormatter, self).__init__(stream_opener, config)
        self.steps = []
        self.show_timings = config.show_timings
        self.show_multiline = config.show_multiline and self.SHOW_MULTI_LINE
        self.show_aligned_keywords = self.SHOW_ALIGNED_KEYWORDS
        self.show_tags = self.SHOW_TAGS
        self.indent_size = self.DEFAULT_INDENT_SIZE
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.printer = ModelPrinter(self.stream)
        # -- LAZY-EVALUATE:
        self._multiline_indentation = None

    @property
    def multiline_indentation(self):
        if self._multiline_indentation is None:
            offset = 0
            if self.show_aligned_keywords:
                offset = 2
            indentation = make_indentation(3 * self.indent_size + offset)
            self._multiline_indentation = indentation
        return self._multiline_indentation

    def reset_steps(self):
        self.steps = []

    def write_tags(self, tags, indent=None):
        if tags and self.show_tags:
            indent = indent or ""
            text = " @".join(tags)
            self.stream.write(u"%s@%s\n" % (indent, text))

    # -- IMPLEMENT-INTERFACE FOR: Formatter
    def feature(self, feature):
        self.reset_steps()
        self.write_tags(feature.tags)
        self.stream.write(u"%s: %s\n" % (feature.keyword, feature.name))

    def background(self, background):
        self.reset_steps()
        indent = make_indentation(self.indent_size)
        text = u"%s%s: %s\n" % (indent, background.keyword, background.name)
        self.stream.write(text)

    def scenario(self, scenario):
        self.reset_steps()
        self.stream.write(u"\n")
        indent = make_indentation(self.indent_size)
        text = u"%s%s: %s\n" % (indent, scenario.keyword, scenario.name)
        self.write_tags(scenario.tags, indent)
        self.stream.write(text)

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        """
        Process the result of a step (after step execution).

        :param step:   Step object with result to process.
        """
        step = self.steps.pop(0)
        indent = make_indentation(2 * self.indent_size)
        if self.show_aligned_keywords:
            # -- RIGHT-ALIGN KEYWORDS (max. keyword width: 6):
            text = u"%s%6s %s ... " % (indent, step.keyword, step.name)
        else:
            text = u"%s%s %s ... " % (indent, step.keyword, step.name)
        self.stream.write(text)

        status_text = step.status.name
        if self.show_timings:
            status_text += " in %0.3fs" % step.duration

        unicode_errors = 0
        if step.error_message:
            try:
                self.stream.write(u"%s\n%s\n" % (status_text, step.error_message))
            except UnicodeError as e:
                unicode_errors += 1
                self.stream.write(u"%s\n" % status_text)
                self.stream.write(u"%s while writing error message: %s\n" % \
                                  (e.__class__.__name__, e))
                if self.RAISE_OUTPUT_ERRORS:
                    raise
        else:
            self.stream.write(u"%s\n" % status_text)

        if self.show_multiline:
            if step.text:
                try:
                    self.doc_string(step.text)
                except UnicodeError as e:
                    unicode_errors += 1
                    self.stream.write(u"%s while writing docstring: %s\n" % \
                                      (e.__class__.__name__, e))
                    if self.RAISE_OUTPUT_ERRORS:
                        raise
            if step.table:
                self.table(step.table)

    def eof(self):
        self.stream.write("\n")

    # -- MORE: Formatter helpers
    def doc_string(self, doc_string):
        self.printer.print_docstring(doc_string, self.multiline_indentation)

    def table(self, table):
        self.printer.print_table(table, self.multiline_indentation)


# -----------------------------------------------------------------------------
# CLASS: Plain0Formatter
# -----------------------------------------------------------------------------
class Plain0Formatter(PlainFormatter):
    """
    Similar to old plain formatter without support for:

      * multi-line text
      * tables
      * tags
    """
    name = "plain0"
    description = "Very basic formatter with maximum compatibility"
    SHOW_MULTI_LINE = False
    SHOW_TAGS = False
    SHOW_ALIGNED_KEYWORDS = False
