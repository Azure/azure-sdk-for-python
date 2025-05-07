from pyrit.models import PromptDataType
from pyrit.prompt_converter import ConverterResult, PromptConverter


class _DefaultConverter(PromptConverter):

    async def convert_async(self, *, prompt: str, input_type: PromptDataType = "text") -> ConverterResult:
        """
        Simple converter that does nothing to the prompt and returns it as is.
        """
        if not self.input_supported(input_type):
            raise ValueError("Input type not supported")

        result = ConverterResult(output_text=prompt, output_type="text")
        return result

    def input_supported(self, input_type: PromptDataType) -> bool:
        return input_type == "text"

    def output_supported(self, output_type: PromptDataType) -> bool:
        return output_type == "text"