# -*- coding: UTF-8 -*-
"""
Provides a formatter that writes prototypes for missing step functions
into a step module file by using step snippets.

NOTE: This is only simplistic, proof-of-concept code.
"""

from __future__ import absolute_import, print_function
from behave.runner_util import make_undefined_step_snippets
from .steps import StepsUsageFormatter


STEP_MODULE_TEMPLATE = '''\
# -*- coding: {encoding} -*-
"""
Missing step implementations (proof-of-concept).
"""

from behave import given, when, then, step

{step_snippets}
'''


class MissingStepsFormatter(StepsUsageFormatter):
    """Formatter that writes missing steps snippets into a step module file.

    Reuses StepsUsageFormatter class because it already contains the logic
    for discovering missing/undefined steps.

    .. code-block:: ini

        # -- FILE: behave.ini
        # NOTE: Long text value needs indentation on following lines.
        [behave.userdata]
        behave.formatter.missing_steps.template = # -*- coding: {encoding} -*-
            # Missing step implementations.
            from behave import given, when, then, step

            {step_snippets}
    """
    name = "missing-steps"
    description = "Writes implementation for missing step definitions."
    template = STEP_MODULE_TEMPLATE
    scope = "behave.formatter.missing_steps"

    def __init__(self, stream_opener, config):
        super(MissingStepsFormatter, self).__init__(stream_opener, config)
        self.template = self.__class__.template
        self.init_from_userdata(config.userdata)

    def init_from_userdata(self, userdata):
        scoped_name = "%s.%s" %(self.scope, "template")
        template_text = userdata.get(scoped_name, self.template)
        self.template = template_text

    def close(self):
        """Called at end of test run.
        NOTE: Overwritten to avoid to truncate/overwrite output-file.
        """
        if self.step_registry and self.undefined_steps:
            # -- ENSURE: Output stream is open.
            self.stream = self.open()
            self.report()

        # -- FINALLY:
        self.close_stream()

    # -- REPORT SPECIFIC-API:
    def report(self):
        """Writes missing step implementations by using step snippets."""
        step_snippets = make_undefined_step_snippets(undefined_steps)
        encoding = self.stream.encoding or "UTF-8"
        function_separator = u"\n\n\n"
        step_snippets_text = function_separator.join(step_snippets)
        module_text = self.template.format(encoding=encoding,
                                           step_snippets=step_snippets_text)
        self.stream.write(module_text)
        self.stream.write("\n")
