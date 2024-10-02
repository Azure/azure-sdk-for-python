# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os


class AIInferenceInstrumentor:
    def str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self):
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")

        var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
        enable_content_tracing = self.str_to_bool(var_value)
        from ._ai_inference_instrumentor_impl import _instrument_inference

        _instrument_inference(enable_content_tracing)

    def uninstrument(self):
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")

        from ._ai_inference_instrumentor_impl import _uninstrument_inference

        _uninstrument_inference()

    def is_instrumented(self):
        from ._ai_inference_instrumentor_impl import _is_instrumented

        return _is_instrumented()
