# -*- coding: UTF-8 -*-
"""
Provides a formatter that provides an overview of available step definitions
(step implementations).
"""

from __future__ import absolute_import
from operator import attrgetter
import inspect
from six.moves import zip
from behave.formatter.base import Formatter
from behave.step_registry import StepRegistry, registry
from behave.textutil import \
    compute_words_maxsize, indent, make_indentation, text as _text
from behave import i18n


# -----------------------------------------------------------------------------
# CLASS: AbstractStepsFormatter
# -----------------------------------------------------------------------------
class AbstractStepsFormatter(Formatter):
    """
    Provides a formatter base class that provides the common functionality
    for formatter classes that operate on step definitions (implementations).

    .. note::
        Supports behave dry-run mode.
    """
    step_types = ("given", "when", "then", "step")

    def __init__(self, stream_opener, config):
        super(AbstractStepsFormatter, self).__init__(stream_opener, config)
        self.step_registry = None
        self.current_feature = None
        self.shows_location = config.show_source

    def reset(self):
        self.step_registry = None
        self.current_feature = None

    def discover_step_definitions(self):
        if self.step_registry is None:
            self.step_registry = StepRegistry()

        for step_type in registry.steps:
            step_definitions = tuple(registry.steps[step_type])
            for step_definition in step_definitions:
                step_definition.step_type = step_type
            self.step_registry.steps[step_type] = step_definitions

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        if not self.step_registry:
            # -- ONLY-ONCE:
            self.discover_step_definitions()

    def eof(self):
        """Called at end of a feature."""
        self.current_feature = None

    def close(self):
        """Called at end of test run."""
        if not self.step_registry:
            self.discover_step_definitions()

        if self.step_registry:
            # -- ENSURE: Output stream is open.
            self.stream = self.open()
            self.report()

        # -- FINALLY:
        self.close_stream()

    # -- REPORT SPECIFIC-API:
    def report(self):
        raise NotImplementedError()

    # pylint: disable=no-self-use
    def describe_step_definition(self, step_definition, step_type=None):
        if not step_type:
            step_type = step_definition.step_type
        assert step_type
        return u"@%s('%s')" % (step_type, step_definition.pattern)


# -----------------------------------------------------------------------------
# CLASS: StepsFormatter
# -----------------------------------------------------------------------------
class StepsFormatter(AbstractStepsFormatter):
    """
    Provides formatter class that provides an overview
    which step definitions are available.

    EXAMPLE:
        $ behave --dry-run -f steps features/
        GIVEN STEP DEFINITIONS[21]:
          Given a new working directory
          Given I use the current directory as working directory
          Given a file named "{filename}" with
          ...
          Given a step passes
          Given a step fails

        WHEN STEP DEFINITIONS[14]:
          When I run "{command}"
          ...
          When a step passes
          When a step fails

        THEN STEP DEFINITIONS[45]:
          Then the command should fail with returncode="{result:int}"
          Then it should pass with
          Then it should fail with
          Then the command output should contain "{text}"
          ...
          Then a step passes
          Then a step fails

        GENERIC STEP DEFINITIONS[13]:
          * I remove the directory "{directory}"
          * a file named "{filename}" exists
          * a file named "{filename}" does not exist
          ...
          * a step passes
          * a step fails

    .. note::
        Supports behave dry-run mode.
    """
    name = "steps"
    description = "Shows step definitions (step implementations)."
    shows_location = True
    min_location_column = 40

    # -- REPORT SPECIFIC-API:
    def report(self):
        self.report_steps_by_type()

    def report_steps_by_type(self):
        """Show an overview of the existing step implementations per step type.
        """
        # pylint: disable=too-many-branches
        assert set(self.step_types) == set(self.step_registry.steps.keys())
        language = self.config.lang or "en"
        language_keywords = i18n.languages[language]

        for step_type in self.step_types:
            steps = list(self.step_registry.steps[step_type])
            if step_type != "step":
                steps.extend(self.step_registry.steps["step"])
            if not steps:
                continue

            # -- PREPARE REPORT: For a step-type.
            step_type_name = step_type.upper()
            if step_type == "step":
                step_keyword = "*"
                step_type_name = "GENERIC"
            else:
                # step_keyword = step_type.capitalize()
                keywords = language_keywords[step_type]
                if keywords[0] == u"*":
                    assert len(keywords) > 1
                    step_keyword = keywords[1]
                else:
                    step_keyword = keywords[0]

            steps_text = [u"%s %s" % (step_keyword, step.pattern)
                          for step in steps]
            if self.shows_location:
                max_size = compute_words_maxsize(steps_text)
                if max_size < self.min_location_column:
                    max_size = self.min_location_column
                schema = u"  %-" + _text(max_size) + "s  # %s\n"
            else:
                schema = u"  %s\n"

            # -- REPORT:
            message = "%s STEP DEFINITIONS[%s]:\n"
            self.stream.write(message % (step_type_name, len(steps)))
            for step, step_text in zip(steps, steps_text):
                if self.shows_location:
                    self.stream.write(schema % (step_text, step.location))
                else:
                    self.stream.write(schema % step_text)
            self.stream.write("\n")


# -----------------------------------------------------------------------------
# CLASS: StepsDocFormatter
# -----------------------------------------------------------------------------
class StepsDocFormatter(AbstractStepsFormatter):
    """
    Provides formatter class that shows the documentation of all registered
    step definitions. The primary purpose is to provide help for a test writer.

    EXAMPLE:
        $ behave --dry-run -f steps.doc features/
        @given('a file named "{filename}" with')
          Function: step_a_file_named_filename_with()
          Location: behave4cmd0/command_steps.py:50
            Creates a textual file with the content provided as docstring.

        @when('I run "{command}"')
          Function: step_i_run_command()
          Location: behave4cmd0/command_steps.py:80
            Run a command as subprocess, collect its output and returncode.

        @step('a file named "{filename}" exists')
          Function: step_file_named_filename_exists()
          Location: behave4cmd0/command_steps.py:305
            Verifies that a file with this filename exists.

            .. code-block:: gherkin

                Given a file named "abc.txt" exists
                 When a file named "abc.txt" exists
        ...

    .. note::
        Supports behave dry-run mode.
    """
    name = "steps.doc"
    description = "Shows documentation for step definitions."
    shows_location = True
    shows_function_name = True
    ordered_by_location = True
    doc_prefix = make_indentation(4)

    # -- REPORT SPECIFIC-API:
    def report(self):
        self.report_step_definition_docs()
        self.stream.write("\n")

    def report_step_definition_docs(self):
        step_definitions = []
        for step_type in self.step_types:
            for step_definition in self.step_registry.steps[step_type]:
                # step_definition.step_type = step_type
                assert step_definition.step_type is not None
                step_definitions.append(step_definition)

        if self.ordered_by_location:
            step_definitions = sorted(step_definitions,
                                      key=attrgetter("location"))

        for step_definition in step_definitions:
            self.write_step_definition(step_definition)

    def write_step_definition(self, step_definition):
        step_definition_text = self.describe_step_definition(step_definition)
        self.stream.write(u"%s\n" % step_definition_text)
        doc = inspect.getdoc(step_definition.func)
        func_name = step_definition.func.__name__
        if self.shows_function_name and func_name not in ("step", "impl"):
            self.stream.write(u"  Function: %s()\n" % func_name)
        if self.shows_location:
            self.stream.write(u"  Location: %s\n" % step_definition.location)
        if doc:
            doc = doc.strip()
            self.stream.write(indent(doc, self.doc_prefix))
            self.stream.write("\n")
        self.stream.write("\n")


# -----------------------------------------------------------------------------
# CLASS: StepsCatalogFormatter
# -----------------------------------------------------------------------------
class StepsCatalogFormatter(StepsDocFormatter):
    """
    Provides formatter class that shows the documentation of all registered
    step definitions. The primary purpose is to provide help for a test writer.

    In order to ease work for non-programmer testers, the technical details of
    the steps (i.e. function name, source location) are ommited and the
    steps are shown as they would apprear in a feature file (no noisy '@',
    or '(', etc.).

    Also, the output is sorted by step type (Given, When, Then)

    Generic step definitions are listed with all three step types.

    EXAMPLE:
        $ behave --dry-run -f steps.catalog features/
        Given a file named "{filename}" with
            Creates a textual file with the content provided as docstring.

        When I run "{command}"
            Run a command as subprocess, collect its output and returncode.

        Given a file named "{filename}" exists
         When a file named "{filename}" exists
         Then a file named "{filename}" exists
            Verifies that a file with this filename exists.

            .. code-block:: gherkin

                Given a file named "abc.txt" exists
                 When a file named "abc.txt" exists
        ...

    .. note::
        Supports behave dry-run mode.
    """
    name = "steps.catalog"
    description = "Shows non-technical documentation for step definitions."
    shows_location = False
    shows_function_name = False
    ordered_by_location = False
    doc_prefix = make_indentation(4)


    def describe_step_definition(self, step_definition, step_type=None):
        if not step_type:
            step_type = step_definition.step_type
        assert step_type
        desc = []
        if step_type == "step":
            for step_type1 in self.step_types[:-1]:
                text = u"%5s %s" % (step_type1.title(), step_definition.pattern)
                desc.append(text)
        else:
            desc.append(u"%s %s" % (step_type.title(), step_definition.pattern))

        return '\n'.join(desc)


# -----------------------------------------------------------------------------
# CLASS: StepsUsageFormatter
# -----------------------------------------------------------------------------
class StepsUsageFormatter(AbstractStepsFormatter):
    """
    Provides formatter class that shows how step definitions are used by steps.

    EXAMPLE:
        $ behave --dry-run -f steps.usage features/
        ...

    .. note::
        Supports behave dry-run mode.
    """
    name = "steps.usage"
    description = "Shows how step definitions are used by steps."
    doc_prefix = make_indentation(4)
    min_location_column = 40

    def __init__(self, stream_opener, config):
        super(StepsUsageFormatter, self).__init__(stream_opener, config)
        self.step_usage_database = {}
        self.undefined_steps = []

    def reset(self):
        super(StepsUsageFormatter, self).reset()
        self.step_usage_database = {}
        self.undefined_steps = []

    # pylint: disable=invalid-name
    def get_step_type_for_step_definition(self, step_definition):
        step_type = step_definition.step_type
        if not step_type:
            # -- DETERMINE STEP-TYPE FROM STEP-REGISTRY:
            assert self.step_registry
            for step_type, values in self.step_registry.steps.items():
                if step_definition in values:
                    return step_type
            # -- OTHERWISE:
            step_type = "step"
        return step_type
    # pylint: enable=invalid-name

    def select_unused_step_definitions(self):
        step_definitions = set()
        for step_type, values in self.step_registry.steps.items():
            step_definitions.update(values)
        used_step_definitions = set(self.step_usage_database.keys())
        unused_step_definitions = step_definitions - used_step_definitions
        return unused_step_definitions

    def update_usage_database(self, step_definition, step):
        matching_steps = self.step_usage_database.get(step_definition, None)
        if matching_steps is None:
            assert step_definition.step_type is not None
            matching_steps = self.step_usage_database[step_definition] = []
        # -- AVOID DUPLICATES: From Scenario Outlines
        if not steps_contain(matching_steps, step):
            matching_steps.append(step)

    def update_usage_database_for_step(self, step):
        step_definition = self.step_registry.find_step_definition(step)
        if step_definition:
            self.update_usage_database(step_definition, step)
        # elif step not in self.undefined_steps:
        elif not steps_contain(self.undefined_steps, step):
            # -- AVOID DUPLICATES: From Scenario Outlines
            self.undefined_steps.append(step)

    # pylint: disable=invalid-name
    def update_usage_database_for_feature(self, feature):
        # -- PROCESS BACKGROUND (if exists): Use Background steps only once.
        if feature.background:
            for step in feature.background.steps:
                self.update_usage_database_for_step(step)

        # -- PROCESS SCENARIOS: Without background steps.
        for scenario in feature.walk_scenarios():
            for step in scenario.steps:
                self.update_usage_database_for_step(step)
    # pylint: enable=invalid-name

    # -- FORMATTER API:
    def feature(self, feature):
        super(StepsUsageFormatter, self).feature(feature)
        self.update_usage_database_for_feature(feature)

    # -- REPORT API:
    def report(self):
        self.report_used_step_definitions()
        self.report_unused_step_definitions()
        self.report_undefined_steps()
        self.stream.write("\n")

    # -- REPORT SPECIFIC-API:
    def report_used_step_definitions(self):
        # -- STEP: Used step definitions.
        # ORDERING: Sort step definitions by file location.
        get_location = lambda x: x[0].location
        step_definition_items = self.step_usage_database.items()
        step_definition_items = sorted(step_definition_items, key=get_location)

        for step_definition, steps in step_definition_items:
            stepdef_text = self.describe_step_definition(step_definition)
            steps_text = [u"  %s %s" % (step.keyword, step.name)
                          for step in steps]
            steps_text.append(stepdef_text)
            max_size = compute_words_maxsize(steps_text)
            if max_size < self.min_location_column:
                max_size = self.min_location_column

            schema = u"%-" + _text(max_size) + "s  # %s\n"
            self.stream.write(schema % (stepdef_text, step_definition.location))
            schema = u"%-" + _text(max_size) + "s  # %s\n"
            for step, step_text in zip(steps, steps_text):
                self.stream.write(schema % (step_text, step.location))
            self.stream.write("\n")

    def report_unused_step_definitions(self):
        unused_step_definitions = self.select_unused_step_definitions()
        if not unused_step_definitions:
            return

        # -- STEP: Prepare report for unused step definitions.
        # ORDERING: Sort step definitions by file location.
        get_location = lambda x: x.location
        step_definitions = sorted(unused_step_definitions, key=get_location)
        step_texts = [self.describe_step_definition(step_definition)
                      for step_definition in step_definitions]

        max_size = compute_words_maxsize(step_texts)
        if max_size < self.min_location_column-2:
            max_size = self.min_location_column-2

        # -- STEP: Write report.
        schema = u"  %-" + _text(max_size) + "s  # %s\n"
        self.stream.write("UNUSED STEP DEFINITIONS[%d]:\n" % len(step_texts))
        for step_definition, step_text in zip(step_definitions, step_texts):
            self.stream.write(schema % (step_text, step_definition.location))

    def report_undefined_steps(self):
        if not self.undefined_steps:
            return

        # -- STEP: Undefined steps.
        undefined_steps = sorted(self.undefined_steps,
                                 key=attrgetter("location"))

        steps_text = [u"  %s %s" % (step.keyword, step.name)
                      for step in undefined_steps]
        max_size = compute_words_maxsize(steps_text)
        if max_size < self.min_location_column:
            max_size = self.min_location_column

        self.stream.write("\nUNDEFINED STEPS[%d]:\n" % len(steps_text))
        schema = u"%-" + _text(max_size) + "s  # %s\n"
        for step, step_text in zip(undefined_steps, steps_text):
            self.stream.write(schema % (step_text, step.location))

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def steps_contain(steps, step):
    for other_step in steps:
        if step == other_step and step.location == other_step.location:
            # -- NOTE: Step comparison does not take location into account.
            return True
    # -- OTHERWISE: Not contained yet (or step in other location).
    return False
