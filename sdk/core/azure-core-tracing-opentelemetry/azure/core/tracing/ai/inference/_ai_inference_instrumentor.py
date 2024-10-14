# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os


class AIInferenceInstrumentor:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
    and provides functionality to check whether instrumentation is active.
    """

    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self):
        """
        Enable instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is already enabled.

        This method checks the environment variable
        'AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED' to determine
        whether to enable content tracing.
        """
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")

        var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
        enable_content_tracing = self._str_to_bool(var_value)
        from ._ai_inference_instrumentor_impl import _instrument_inference

        _instrument_inference(enable_content_tracing)

    def uninstrument(self):
        """
        Disable instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is not currently enabled.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")

        from ._ai_inference_instrumentor_impl import _uninstrument_inference

        _uninstrument_inference()

    def is_instrumented(self):
        """
        Check if instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        from ._ai_inference_instrumentor_impl import _is_instrumented

        return _is_instrumented()
