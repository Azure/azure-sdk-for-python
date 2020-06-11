# -*- coding: utf-8 -*-
"""
Provides 2 dotted progress formatters:

  * ScenarioProgressFormatter (scope: scenario)
  * StepProgressFormatter (scope: step)

A "dot" character that represents the result status is printed after
executing a scope item.
"""

from __future__ import absolute_import
import six
from behave.formatter.base import Formatter
from behave.model_core import Status
from behave.textutil import text as _text


# -----------------------------------------------------------------------------
# CLASS: ProgressFormatterBase
# -----------------------------------------------------------------------------
class ProgressFormatterBase(Formatter):
    """
    Provides formatter base class for different variants of progress formatters.
    A progress formatter show an abbreviated, compact dotted progress bar,
    similar to unittest output (in terse mode).
    """
    # -- MAP: step.status to short dot_status representation.
    dot_status = {
        "passed":    ".",
        "failed":    "F",
        "error":     "E",   # Caught exception, but not an AssertionError
        "skipped":   "S",
        "untested":  "_",
        "undefined": "U",
    }
    show_timings = False

    def __init__(self, stream_opener, config):
        super(ProgressFormatterBase, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.steps = []
        self.failures = []
        self.current_feature = None
        self.current_scenario = None
        self.show_timings = config.show_timings and self.show_timings

    def reset(self):
        self.steps = []
        self.failures = []
        self.current_feature = None
        self.current_scenario = None

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        self.stream.write("%s  " % six.text_type(feature.filename))
        self.stream.flush()

    def background(self, background):
        pass

    def scenario(self, scenario):
        """
        Process the next scenario.
        But first allow to report the status on the last scenario.
        """
        self.report_scenario_completed()
        self.current_scenario = scenario

    def step(self, step):
        self.steps.append(step)

    def result(self, step):
        self.steps.pop(0)
        self.report_step_progress(step)

    def eof(self):
        """
        Called at end of a feature.
        It would be better to have a hook that is called after all features.
        """
        self.report_scenario_completed()
        self.report_feature_completed()
        self.report_failures()
        self.stream.flush()
        self.reset()

    # -- SPECIFIC PART:
    def report_step_progress(self, step):
        """Report the progress on the current step.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_scenario_progress(self):
        """Report the progress for the current/last scenario.
        The default implementation is empty.
        It should be override by a concrete class.
        """
        pass

    def report_feature_completed(self):
        """Hook called when a feature is completed to perform the last tasks.
        """
        pass

    def report_scenario_completed(self):
        """Hook called when a scenario is completed to perform the last tasks.
        """
        self.report_scenario_progress()

    def report_feature_duration(self):
        if self.show_timings and self.current_feature:
            self.stream.write(u"  # %.3fs" % self.current_feature.duration)
        self.stream.write("\n")

    def report_scenario_duration(self):
        if self.show_timings and self.current_scenario:
            self.stream.write(u"  # %.3fs" % self.current_scenario.duration)
        self.stream.write("\n")

    def report_failures(self):
        if self.failures:
            separator = "-" * 80
            self.stream.write(u"%s\n" % separator)
            for step in self.failures:
                self.stream.write(u"FAILURE in step '%s':\n" % step.name)
                self.stream.write(u"  Feature:  %s\n" % step.feature.name)
                self.stream.write(u"  Scenario: %s\n" % step.scenario.name)
                self.stream.write(u"%s\n" % step.error_message)
                if step.exception:
                    self.stream.write(u"exception: %s\n" % step.exception)
            self.stream.write(u"%s\n" % separator)


# -----------------------------------------------------------------------------
# CLASS: ScenarioProgressFormatter
# -----------------------------------------------------------------------------
class ScenarioProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each scenario similar to unittest.
    """
    name = "progress"
    description = "Shows dotted progress for each executed scenario."

    def report_scenario_progress(self):
        """
        Report the progress for the current/last scenario.
        """
        if not self.current_scenario:
            return  # SKIP: No results to report for first scenario.
        # -- NORMAL-CASE:
        status_name = self.current_scenario.status.name
        dot_status = self.dot_status[status_name]
        if status_name == "failed":
            # MAYBE TODO: self.failures.append(result)
            pass
        self.stream.write(dot_status)
        self.stream.flush()

    def report_feature_completed(self):
        self.report_feature_duration()

# -----------------------------------------------------------------------------
# CLASS: StepProgressFormatter
# -----------------------------------------------------------------------------
class StepProgressFormatter(ProgressFormatterBase):
    """
    Report dotted progress for each step similar to unittest.
    """
    name = "progress2"
    description = "Shows dotted progress for each executed step."

    def report_step_progress(self, step):
        """Report the progress for each step."""
        dot_status = self.dot_status[step.status.name]
        if step.status == Status.failed:
            if (step.exception and
                    not isinstance(step.exception, AssertionError)):
                # -- ISA-ERROR: Some Exception
                dot_status = self.dot_status["error"]
            step.feature = self.current_feature
            step.scenario = self.current_scenario
            self.failures.append(step)
        self.stream.write(dot_status)
        self.stream.flush()

    def report_feature_completed(self):
        self.report_feature_duration()


# -----------------------------------------------------------------------------
# CLASS: ScenarioStepProgressFormatter
# -----------------------------------------------------------------------------
class ScenarioStepProgressFormatter(StepProgressFormatter):
    """
    Shows detailed dotted progress for both each step of a scenario.
    Differs from StepProgressFormatter by:

      * showing scenario names (as prefix scenario step progress)
      * showing failures after each scenario (if necessary)

    EXAMPLE:
        $ behave -f progress3 features
        Feature with failing scenario    # features/failing_scenario.feature
            Simple scenario with last failing step  ....F
        -----------------------------------------------------------------------
        FAILURE in step 'last step fails' (features/failing_scenario.feature:7):
        Assertion Failed: xxx
        -----------------------------------------------------------------------
    """
    name = "progress3"
    description = "Shows detailed progress for each step of a scenario."
    indent_size = 2
    scenario_prefix = " " * indent_size

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature
        self.stream.write(u"%s    # %s" % (feature.name, feature.filename))

    def scenario(self, scenario):
        """Process the next scenario."""
        # -- LAST SCENARIO: Report failures (if any).
        self.report_scenario_completed()

        # -- NEW SCENARIO:
        assert not self.failures
        self.current_scenario = scenario
        scenario_name = scenario.name
        if scenario_name:
            scenario_name += " "
        self.stream.write(u"%s%s " % (self.scenario_prefix, scenario_name))
        self.stream.flush()

    # -- DISABLED:
    # def eof(self):
    #     has_scenarios = self.current_feature and self.current_scenario
    #     super(ScenarioStepProgressFormatter, self).eof()
    #     if has_scenarios:
    #         # -- EMPTY-LINE between 2 features.
    #         self.stream.write("\n")

    # -- PROGRESS FORMATTER DETAILS:
    # @overriden
    def report_feature_completed(self):
        # -- SKIP: self.report_feature_duration()
        has_scenarios = self.current_feature and self.current_scenario
        if has_scenarios:
            # -- EMPTY-LINE between 2 features.
            self.stream.write("\n")

    def report_scenario_completed(self):
        self.report_scenario_progress()
        self.report_scenario_duration()
        self.report_failures()
        self.failures = []

    def report_failures(self):
        if self.failures:
            separator = "-" * 80
            self.stream.write(u"%s\n" % separator)
            unicode_errors = 0
            for step in self.failures:
                try:
                    self.stream.write(u"FAILURE in step '%s' (%s):\n" % \
                                      (step.name, step.location))
                    self.stream.write(u"%s\n" % step.error_message)
                    self.stream.write(u"%s\n" % separator)
                except UnicodeError as e:
                    self.stream.write(u"%s while reporting failure in %s\n" % \
                                      (e.__class__.__name__, step.location))
                    self.stream.write(u"ERROR: %s\n" % \
                                      _text(e, encoding=self.stream.encoding))
                    unicode_errors += 1

            if unicode_errors:
                msg = u"HINT: %d unicode errors occured during failure reporting.\n"
                self.stream.write(msg % unicode_errors)
            self.stream.flush()
