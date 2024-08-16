# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from .azure_telemetry_instrumentor import AzureTelemetryInstrumentor
 
class AiInferenceApiInstrumentor(AzureTelemetryInstrumentor):
    def __init__(self):
        super().__init__()

    def str_to_bool(self, s):
        if s is None:  
            return False  
        return str(s).lower() == 'true'

    def instrument(self):
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")
        
        var_value = os.environ.get("AZURE_INFERENCE_API_ENABLE_CONTENT_TRACING")
        enable_content_tracing = self.str_to_bool(var_value)
        from ._inference_api_instrumentor_impl import _inject_inference_api
        _inject_inference_api(enable_content_tracing)

    def uninstrument(self):
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")

        from ._inference_api_instrumentor_impl import _restore_inference_api
        _restore_inference_api()

    def is_instrumented(self):
        from ._inference_api_instrumentor_impl import _is_instrumented
        return _is_instrumented()
