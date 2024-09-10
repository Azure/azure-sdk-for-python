# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod  
  
class AzureTelemetryInstrumentor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def instrument(self):
        pass

    @abstractmethod
    def uninstrument(self):
        pass

    @abstractmethod
    def is_instrumented(self):
        pass