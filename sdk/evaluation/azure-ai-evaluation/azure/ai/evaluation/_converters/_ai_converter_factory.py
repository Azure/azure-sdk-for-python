import azure.ai.projects as aap
from azure.ai.evaluation import LegacyAgentConverter, FDPAgentConverter
from azure.ai.projects import AIProjectClient
from packaging.version import Version

from azure.ai.evaluation._common._experimental import experimental

@experimental
class AIAgentConverterFactory:

    """Factory class to create the appropriate agent converter based on the version of the AI service."""

    @staticmethod
    def get_converter(project_client: AIProjectClient):
        if project_client is None:
            return None
        if Version(aap.__version__) > Version("1.0.0b10") or aap.__version__.startswith("1.0.0a"):
            return FDPAgentConverter(project_client=project_client)
        else:
            return LegacyAgentConverter(project_client=project_client)
