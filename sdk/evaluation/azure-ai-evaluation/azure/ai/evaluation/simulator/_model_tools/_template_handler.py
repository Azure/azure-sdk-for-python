# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Optional, TypedDict, cast, Union
from ast import literal_eval
from typing_extensions import NotRequired

from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._common.onedp._client import AIProjectClient

from ._rai_client import RAIClient

CONTENT_HARM_TEMPLATES_COLLECTION_KEY = {
    "adv_qa",
    "adv_conversation",
    "adv_summarization",
    "adv_search",
    "adv_rewrite",
    "adv_content_gen_ungrounded",
    "adv_content_gen_grounded",
    "adv_content_protected_material",
    "adv_politics",
}


class TemplateParameters(TypedDict):
    """Parameters used in Templates

    .. note::

        This type is good enough to type check, but is incorrect. It's meant to represent a dictionary with a known
        `metadata` key (Dict[str, str]), a known `ch_template_placeholder` key (str), and an unknown number of keys
        that map to `str` values.

        In typescript, this type would be spelled:

        .. code-block:: typescript

            type AdversarialTemplateParameters = {
                [key: string]: string
                ch_template_placeholder: string
                metadata: {[index: string]: string} # Doesn't typecheck but gets the point across
            }

        At time of writing, this isn't possible to express with a TypedDict. TypedDicts must be "closed" in that
        they fully specify all the keys they can contain.

        `PEP 728 – TypedDict with Typed Extra Items <https://peps.python.org/pep-0728/>` is a proposal to support
        this, but would only be available in Python 3.13 at the earliest.
    """

    metadata: Dict[str, str]
    conversation_starter: str
    ch_template_placeholder: str
    group_of_people: NotRequired[str]
    category: NotRequired[str]
    target_population: NotRequired[str]
    topic: NotRequired[str]
    jailbreak_string: NotRequired[str]


class _CategorizedParameter(TypedDict):
    parameters: List[TemplateParameters]
    category: str
    parameters_key: str


class ContentHarmTemplatesUtils:
    """Content harm templates utility functions."""

    @staticmethod
    def get_template_category(key: str) -> str:
        """Parse category from template key

        :param key: The template key
        :type key: str
        :return: The category
        :rtype: str
        """
        # Check for datasets whose names do not align with the normal
        # naming convention where the first segment of the name is the category.
        if key == "conversation/public/ip/bing_ip.json":
            return "content_protected_material"
        return key.split("/")[0]

    @staticmethod
    def get_template_key(key: str) -> str:
        """Given a template dataset name (which looks like a .json file name) convert it into
        the corresponding template key (which looks like a .md file name). This allows us to
        properly link datasets to the LLM that must be used to simulate them.

        :param key: The dataset key.
        :type key: str
        :return: The template key.
        :rtype: str
        """
        filepath = key.rsplit(".json")[0]
        parts = str(filepath).split("/")
        filename = ContentHarmTemplatesUtils.json_name_to_md_name(parts[-1])
        prefix = parts[:-1]
        prefix.append(filename)

        return "/".join(prefix)

    @staticmethod
    def json_name_to_md_name(name) -> str:
        """Convert JSON filename to Markdown filename

        :param name: The JSON filename
        :type name: str
        :return: The Markdown filename
        :rtype: str
        """
        result = name.replace("_aml", "")

        return result + ".md"


class AdversarialTemplate:
    """Template for adversarial scenarios.

    :param template_name: The name of the template.
    :type template_name: str
    :param text: The template text.
    :type text: str
    :param context_key: The context key.
    :param template_parameters: The template parameters.
    """

    def __init__(
        self,
        template_name: str,
        text: Optional[str],
        context_key: List,
        template_parameters: Optional[List[TemplateParameters]] = None,
    ) -> None:
        self.text = text
        self.context_key = context_key
        self.template_name = template_name
        self.template_parameters = template_parameters or []

    def __str__(self) -> str:
        return "{{ch_template_placeholder}}"


class AdversarialTemplateHandler:
    """
    Initialize the AdversarialTemplateHandler.

    :param azure_ai_project: The Azure AI project, which can either be a string representing the project endpoint 
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name. 
    :type azure_ai_project: Union[str, AzureAIProject]
    :param rai_client: The RAI client or AI Project client used for fetching parameters.
    :type rai_client: Union[~azure.ai.evaluation.simulator._model_tools.RAIClient, ~azure.ai.evaluation._common.onedp._client.AIProjectClient]
    """

    def __init__(self, azure_ai_project: Union[str, AzureAIProject], rai_client: Union[RAIClient, AIProjectClient]) -> None:
        self.azure_ai_project = azure_ai_project
        self.categorized_ch_parameters: Optional[Dict[str, _CategorizedParameter]] = None
        self.rai_client = rai_client

    async def _get_content_harm_template_collections(self, collection_key: str) -> List[AdversarialTemplate]:
        if self.categorized_ch_parameters is None:
            categorized_parameters: Dict[str, _CategorizedParameter] = {}
            util = ContentHarmTemplatesUtils

            if isinstance(self.rai_client, RAIClient):
                parameters = await self.rai_client.get_contentharm_parameters()
            elif isinstance(self.rai_client, AIProjectClient):
                parameters = literal_eval(self.rai_client.red_teams.get_template_parameters())
            
            for k in parameters.keys():
                template_key = util.get_template_key(k)
                categorized_parameters[template_key] = {
                    "parameters": cast(List[TemplateParameters], parameters[k]),
                    "category": util.get_template_category(k),
                    "parameters_key": k,
                }
            self.categorized_ch_parameters = categorized_parameters

        template_category = collection_key.split("adv_")[-1]

        plist = self.categorized_ch_parameters
        ch_templates = []
        for key, value in plist.items():
            if value["category"] == template_category:
                params = value["parameters"]
                for p in params:
                    p.update({"ch_template_placeholder": "{{ch_template_placeholder}}"})

                template = AdversarialTemplate(template_name=key, text=None, context_key=[], template_parameters=params)

                ch_templates.append(template)
        return ch_templates

    def get_template(self, template_name: str) -> Optional[AdversarialTemplate]:
        """Generate content harm template.

        :param template_name: The name of the template.
        :type template_name: str
        :return: The generated content harm template.
        :rtype: Optional[~azure.ai.evaluation.simulator._model_tools.AdversarialTemplate]
        """
        if template_name in CONTENT_HARM_TEMPLATES_COLLECTION_KEY:
            return AdversarialTemplate(template_name=template_name, text=None, context_key=[], template_parameters=None)
        return None
