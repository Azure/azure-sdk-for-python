# -*- coding: UTF-8 -*-

from __future__ import absolute_import, with_statement
import re
import sys
import six
from behave import model, i18n
from behave.textutil import text as _text


DEFAULT_LANGUAGE = "en"


def parse_file(filename, language=None):
    with open(filename, "rb") as f:
        # file encoding is assumed to be utf8. Oh, yes.
        data = f.read().decode("utf8")
    return parse_feature(data, language, filename)


def parse_feature(data, language=None, filename=None):
    # ALL data operated on by the parser MUST be unicode
    assert isinstance(data, six.text_type)

    try:
        result = Parser(language).parse(data, filename)
    except ParserError as e:
        e.filename = filename
        raise

    return result

def parse_steps(text, language=None, filename=None):
    """
    Parse a number of steps a multi-line text from a scenario.
    Scenario line with title and keyword is not provided.

    :param text: Multi-line text with steps to parse (as unicode).
    :param language:  i18n language identifier (optional).
    :param filename:  Filename (optional).
    :return: Parsed steps (if successful).
    """
    assert isinstance(text, six.text_type)
    try:
        result = Parser(language, variant="steps").parse_steps(text, filename)
    except ParserError as e:
        e.filename = filename
        raise
    return result

def parse_tags(text):
    """
    Parse tags from text (one or more lines, as string).

    :param text: Multi-line text with tags to parse (as unicode).
    :return: List of tags (if successful).
    """
    # assert isinstance(text, unicode)
    if not text:
        return []
    return Parser(variant="tags").parse_tags(text)


class ParserError(Exception):
    def __init__(self, message, line, filename=None, line_text=None):
        if line:
            message += u" at line %d" % line
            if line_text:
                message += u': "%s"' % line_text.strip()
        super(ParserError, self).__init__(message)
        self.line = line
        self.line_text = line_text
        self.filename = filename

    def __str__(self):
        arg0 = _text(self.args[0])
        if self.filename:
            filename = _text(self.filename, sys.getfilesystemencoding())
            return u'Failed to parse "%s": %s' % (filename, arg0)
        else:
            return u"Failed to parse <string>: %s" % arg0

    if six.PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.__unicode__().encode("utf-8")


class Parser(object):
    """Feature file parser for behave."""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, language=None, variant=None):
        if not variant:
            variant = "feature"
        self.language = language
        self.variant = variant
        self.state = "init"
        self.line = 0
        self.last_step = None
        self.multiline_start = None
        self.multiline_leading = None
        self.multiline_terminator = None

        self.filename = None
        self.feature = None
        self.statement = None
        self.tags = []
        self.lines = []
        self.table = None
        self.examples = None
        self.keywords = None
        if self.language:
            self.keywords = i18n.languages[self.language]
        # NOT-NEEDED: self.reset()

    def reset(self):
        # This can probably go away.
        if self.language:
            self.keywords = i18n.languages[self.language]
        else:
            self.keywords = None

        self.state = "init"
        self.line = 0
        self.last_step = None
        self.multiline_start = None
        self.multiline_leading = None
        self.multiline_terminator = None

        self.filename = None
        self.feature = None
        self.statement = None
        self.tags = []
        self.lines = []
        self.table = None
        self.examples = None

    def parse(self, data, filename=None):
        self.reset()

        self.filename = filename

        for line in data.split("\n"):
            self.line += 1
            if not line.strip() and self.state != "multiline":
                # -- SKIP EMPTY LINES, except in multiline string args.
                continue
            self.action(line)

        if self.table:
            self.action_table("")

        feature = self.feature
        if feature:
            feature.parser = self
        self.reset()
        return feature

    def _build_feature(self, keyword, line):
        name = line[len(keyword) + 1:].strip()
        language = self.language or DEFAULT_LANGUAGE
        self.feature = model.Feature(self.filename, self.line, keyword,
                                     name, tags=self.tags, language=language)
        # -- RESET STATE:
        self.tags = []

    def _build_background_statement(self, keyword, line):
        if self.tags:
            msg = u"Background supports no tags: @%s" % (u" @".join(self.tags))
            raise ParserError(msg, self.line, self.filename, line)
        name = line[len(keyword) + 1:].strip()
        statement = model.Background(self.filename, self.line, keyword, name)
        self.statement = statement
        self.feature.background = self.statement

    def _build_scenario_statement(self, keyword, line):
        name = line[len(keyword) + 1:].strip()
        self.statement = model.Scenario(self.filename, self.line,
                                        keyword, name, tags=self.tags)
        self.feature.add_scenario(self.statement)
        # -- RESET STATE:
        self.tags = []

    def _build_scenario_outline_statement(self, keyword, line):
        # pylint: disable=C0103
        #   C0103   Invalid name "build_scenario_outline_statement", too long.
        name = line[len(keyword) + 1:].strip()
        self.statement = model.ScenarioOutline(self.filename, self.line,
                                               keyword, name, tags=self.tags)
        self.feature.add_scenario(self.statement)
        # -- RESET STATE:
        self.tags = []

    def _build_examples(self, keyword, line):
        if not isinstance(self.statement, model.ScenarioOutline):
            message = u"Examples must only appear inside scenario outline"
            raise ParserError(message, self.line, self.filename, line)
        name = line[len(keyword) + 1:].strip()
        self.examples = model.Examples(self.filename, self.line,
                                       keyword, name, tags=self.tags)
        # pylint: disable=E1103
        #   E1103   Instance of "Background" has no "examples" member
        #           (but some types could not be inferred).
        self.statement.examples.append(self.examples)

        # -- RESET STATE:
        self.tags = []


    def diagnose_feature_usage_error(self):
        if self.feature:
            return "Multiple features in one file are not supported."
        else:
            return "Feature should not be used here."

    def diagnose_background_usage_error(self):
        if self.feature and self.feature.scenarios:
            return "Background may not occur after Scenario/ScenarioOutline."
        elif self.tags:
            return "Background does not support tags."
        else:
            return "Background should not be used here."

    def diagnose_scenario_usage_error(self):
        if not self.feature:
            return "Scenario may not occur before Feature."
        else:
            return "Scenario should not be used here."

    def diagnose_scenario_outline_usage_error(self): # pylint: disable=invalid-name
        if not self.feature:
            return "ScenarioOutline may not occur before Feature."
        else:
            return "ScenarioOutline should not be used here."

    def ask_parse_failure_oracle(self, line):
        """
        Try to find the failure reason when a parse failure occurs:

            Oracle, oracle, ... what went wrong?
            Zzzz

        :param line:  Text line where parse failure occured (as string).
        :return: Reason (as string) if an explanation is found.
                 Otherwise, empty string or None.
        """
        feature_kwd = self.match_keyword("feature", line)
        if feature_kwd:
            return self.diagnose_feature_usage_error()
        background_kwd = self.match_keyword("background", line)
        if background_kwd:
            return self.diagnose_background_usage_error()
        scenario_kwd = self.match_keyword("scenario", line)
        if scenario_kwd:
            return self.diagnose_scenario_usage_error()
        scenario_outline_kwd = self.match_keyword("scenario_outline", line)
        if scenario_outline_kwd:
            return self.diagnose_scenario_outline_usage_error()
        # -- OTHERWISE:
        if self.variant == "feature" and not self.feature:
            return "No feature found."
        # -- FINALLY: No glue what went wrong.
        return None

    def action(self, line):
        if line.strip().startswith("#") and self.state != "multiline":
            if self.state != "init" or self.tags or self.variant != "feature":
                return

            # -- DETECT: language comment (at begin of feature file; state=init)
            line = line.strip()[1:].strip()
            if line.lstrip().lower().startswith("language:"):
                language = line[9:].strip()
                self.language = language
                self.keywords = i18n.languages[language]
            return

        func = getattr(self, "action_" + self.state, None)
        if func is None:
            line = line.strip()
            msg = u"Parser in unknown state %s;" % self.state
            raise ParserError(msg, self.line, self.filename, line)
        if not func(line):
            line = line.strip()
            msg = u'\nParser failure in state %s, at line %d: "%s"\n' % \
                  (self.state, self.line, line)
            reason = self.ask_parse_failure_oracle(line)
            if reason:
                msg += u"REASON: %s" % reason
            raise ParserError(msg, None, self.filename)

    def action_init(self, line):
        line = line.strip()
        if line.startswith("@"):
            self.tags.extend(self.parse_tags(line))
            return True

        feature_kwd = self.match_keyword("feature", line)
        if feature_kwd:
            self._build_feature(feature_kwd, line)
            self.state = "feature"
            return True
        return False

    # def subaction_detect_next_scenario(self, line):
    #     if line.startswith("@"):
    #         self.tags.extend(self.parse_tags(line))
    #         self.state = "next_scenario"
    #         return True
    #
    #     scenario_kwd = self.match_keyword("scenario", line)
    #     if scenario_kwd:
    #         self._build_scenario_statement(scenario_kwd, line)
    #         self.state = "scenario"
    #         return True
    #
    #     scenario_outline_kwd = self.match_keyword("scenario_outline", line)
    #     if scenario_outline_kwd:
    #         self._build_scenario_outline_statement(scenario_outline_kwd, line)
    #         self.state = "scenario"
    #         return True
    #
    #     # -- OTHERWISE:
    #     return False

    # pylint: disable=invalid-name
    def subaction_detect_taggable_statement(self, line):
        """Subaction is used after first tag line is detected.
        Additional lines with tags or taggable_statement follow.

        Taggable statements (excluding Feature) are:
        * Scenario
        * ScenarioOutline
        * Examples (within ScenarioOutline)
        """
        if line.startswith("@"):
            self.tags.extend(self.parse_tags(line))
            self.state = "taggable_statement"
            return True

        scenario_kwd = self.match_keyword("scenario", line)
        if scenario_kwd:
            self._build_scenario_statement(scenario_kwd, line)
            self.state = "scenario"
            return True

        scenario_outline_kwd = self.match_keyword("scenario_outline", line)
        if scenario_outline_kwd:
            self._build_scenario_outline_statement(scenario_outline_kwd, line)
            self.state = "scenario"
            return True

        examples_kwd = self.match_keyword("examples", line)
        if examples_kwd:
            self._build_examples(examples_kwd, line)
            self.state = "table"
            return True

        # -- OTHERWISE:
        return False
    # pylint: enable=invalid-name

    def action_feature(self, line):
        line = line.strip()
        # OLD: if self.subaction_detect_next_scenario(line):
        if self.subaction_detect_taggable_statement(line):
            # -- DETECTED: Next Scenario, ScenarioOutline (or tags)
            return True

        background_kwd = self.match_keyword("background", line)
        if background_kwd:
            self._build_background_statement(background_kwd, line)
            self.state = "steps"
            return True

        self.feature.description.append(line)
        return True

    # def action_next_scenario(self, line):
    #     """
    #     Entered after first tag for Scenario/ScenarioOutline is detected.
    #     """
    #     line = line.strip()
    #     if self.subaction_detect_next_scenario(line):
    #         return True
    #
    #     return False

    def action_taggable_statement(self, line):
        """Entered after first tag for Scenario/ScenarioOutline or
        Examples is detected (= taggable_statement except Feature).

        Taggable statements (excluding Feature) are:
          * Scenario
          * ScenarioOutline
          * Examples (within ScenarioOutline)
        """
        line = line.strip()
        if self.subaction_detect_taggable_statement(line):
            # -- DETECTED: Next Scenario, ScenarioOutline or Examples (or tags)
            return True

        return False

    def action_scenario(self, line):
        """
        Entered when Scenario/ScenarioOutline keyword/line is detected.
        Hunts/collects scenario description lines.

        DETECT:
            * first step of Scenario/ScenarioOutline
            * next Scenario/ScenarioOutline.
        """
        line = line.strip()
        step = self.parse_step(line)
        if step:
            # -- FIRST STEP DETECTED: End collection of scenario descriptions.
            self.state = "steps"
            self.statement.steps.append(step)
            return True

        # -- CASE: Detect next Scenario/ScenarioOutline
        #   * Scenario with scenario description, but without steps.
        #   * Title-only scenario without scenario description and steps.
        # OLD: if self.subaction_detect_next_scenario(line):
        if self.subaction_detect_taggable_statement(line):
            # -- DETECTED: Next Scenario, ScenarioOutline (or tags)
            return True

        # -- OTHERWISE: Add scenario description line.
        # pylint: disable=E1103
        #   E1103   Instance of "Background" has no "description" member...
        self.statement.description.append(line)
        return True

    def action_steps(self, line):
        """
        Entered when first step is detected (or nested step parsing).

        Subcases:
          * step
          * multi-line text (doc-string), following a step
          * table, following a step
          * examples for a ScenarioOutline, after ScenarioOutline steps

        DETECT:
          * next Scenario/ScenarioOutline or Examples (in a ScenarioOutline)
        """
        # pylint: disable=R0911
        #   R0911   Too many return statements (8/6)
        stripped = line.lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            self.state = "multiline"
            self.multiline_start = self.line
            self.multiline_terminator = stripped[:3]
            self.multiline_leading = line.index(stripped[0])
            return True

        line = line.strip()
        step = self.parse_step(line)
        if step:
            self.statement.steps.append(step)
            return True

        if self.subaction_detect_taggable_statement(line):
            # -- DETECTED: Next Scenario, ScenarioOutline or Examples (or tags)
            return True

        if line.startswith("|"):
            assert self.statement.steps, "TABLE-START without step detected."
            self.state = "table"
            return self.action_table(line)

        return False

    def action_multiline(self, line):
        if line.strip().startswith(self.multiline_terminator):
            step = self.statement.steps[-1]
            step.text = model.Text(u"\n".join(self.lines), u"text/plain",
                                   self.multiline_start)
            if step.name.endswith(":"):
                step.name = step.name[:-1]
            self.lines = []
            self.multiline_terminator = None
            self.state = "steps"
            return True

        self.lines.append(line[self.multiline_leading:])
        # -- BETTER DIAGNOSTICS: May remove non-whitespace in execute_steps()
        removed_line_prefix = line[:self.multiline_leading]
        if removed_line_prefix.strip():
            message = u"BAD-INDENT in multiline text: "
            message += u"Line '%s' would strip leading '%s'" % \
                        (line, removed_line_prefix)
            raise ParserError(message, self.line, self.filename)
        return True

    def action_table(self, line):
        line = line.strip()

        if not line.startswith("|"):
            if self.examples:
                self.examples.table = self.table
                self.examples = None
            else:
                step = self.statement.steps[-1]
                step.table = self.table
                if step.name.endswith(":"):
                    step.name = step.name[:-1]
            self.table = None
            self.state = "steps"
            return self.action_steps(line)

        # -- SUPPORT: Escaped-pipe(s) in Gherkin cell values.
        #    Search for pipe(s) that are not preceeded with an escape char.
        cells = [cell.replace("\\|", "|").strip()
                 for cell in re.split(r"(?<!\\)\|", line[1:-1])]
        if self.table is None:
            self.table = model.Table(cells, self.line)
        else:
            if len(cells) != len(self.table.headings):
                raise ParserError(u"Malformed table", self.line)
            self.table.add_row(cells, self.line)
        return True

    def match_keyword(self, keyword, line):
        if not self.keywords:
            self.language = DEFAULT_LANGUAGE
            self.keywords = i18n.languages[DEFAULT_LANGUAGE]
        for alias in self.keywords[keyword]:
            if line.startswith(alias + ":"):
                return alias
        return False

    def parse_tags(self, line):
        """
        Parse a line with one or more tags:

          * A tag starts with the AT sign.
          * A tag consists of one word without whitespace chars.
          * Multiple tags are separated with whitespace chars
          * End-of-line comment is stripped.

        :param line:   Line with one/more tags to process.
        :raise ParserError: If syntax error is detected.
        """
        assert line.startswith("@")
        tags = []
        for word in line.split():
            if word.startswith("@"):
                tags.append(model.Tag(word[1:], self.line))
            elif word.startswith("#"):
                break   # -- COMMENT: Skip rest of line.
            else:
                # -- BAD-TAG: Abort here.
                raise ParserError(u"tag: %s (line: %s)" % (word, line),
                                  self.line, self.filename)
        return tags

    def parse_step(self, line):
        for step_type in ("given", "when", "then", "and", "but"):
            for kw in self.keywords[step_type]:
                if kw.endswith("<"):
                    whitespace = ""
                    kw = kw[:-1]
                else:
                    whitespace = " "

                # try to match the keyword; also attempt a purely lowercase
                # match if that'll work
                if not (line.startswith(kw + whitespace)
                        or line.lower().startswith(kw.lower() + whitespace)):
                    continue

                name = line[len(kw):].strip()
                if step_type in ("and", "but"):
                    if not self.last_step:
                        raise ParserError(u"No previous step", self.line)
                    step_type = self.last_step
                else:
                    self.last_step = step_type
                step = model.Step(self.filename, self.line, kw, step_type,
                                  name)
                return step
        return None

    def parse_steps(self, text, filename=None):
        """
        Parse support for execute_steps() functionality that supports step with:
          * multiline text
          * table

        :param text:  Text that contains 0..* steps
        :return: List of parsed steps (as model.Step objects).
        """
        assert isinstance(text, six.text_type)
        if not self.language:
            self.language = DEFAULT_LANGUAGE
        self.reset()
        self.filename = filename
        self.statement = model.Scenario(filename, 0, u"scenario", u"")
        self.state = "steps"

        for line in text.split("\n"):
            self.line += 1
            if not line.strip() and self.state != "multiline":
                # -- SKIP EMPTY LINES, except in multiline string args.
                continue
            self.action(line)

        # -- FINALLY:
        if self.table:
            self.action_table("")
        steps = self.statement.steps
        return steps
