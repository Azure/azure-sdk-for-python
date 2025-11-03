# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Optional


class IdGenerator(ABC):
    @abstractmethod
    def generate(self, category: Optional[str] = None) -> str: ...

    def generate_function_call_id(self) -> str:
        return self.generate("func")

    def generate_function_output_id(self) -> str:
        return self.generate("funcout")

    def generate_message_id(self) -> str:
        return self.generate("msg")
