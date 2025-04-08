# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from azure.ai.evaluation._common._experimental import experimental

# cspell:ignore vuln
@experimental
class AdversarialScenario(Enum):
    """Adversarial scenario types

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START adversarial_scenario]
            :end-before: [END adversarial_scenario]
            :language: python
            :dedent: 8
            :caption: Configure an AdversarialSimulator with an Adversarial Conversation scenario.
    """

    ADVERSARIAL_QA = "adv_qa"
    ADVERSARIAL_CONVERSATION = "adv_conversation"
    ADVERSARIAL_SUMMARIZATION = "adv_summarization"
    ADVERSARIAL_SEARCH = "adv_search"
    ADVERSARIAL_REWRITE = "adv_rewrite"
    ADVERSARIAL_CONTENT_GEN_UNGROUNDED = "adv_content_gen_ungrounded"
    ADVERSARIAL_CONTENT_GEN_GROUNDED = "adv_content_gen_grounded"
    ADVERSARIAL_CONTENT_PROTECTED_MATERIAL = "adv_content_protected_material"
    ADVERSARIAL_CODE_VULNERABILITY = "adv_code_vuln"
    ADVERSARIAL_UNGROUNDED_ATTRIBUTES = "adv_isa"


@experimental
class AdversarialScenarioJailbreak(Enum):
    """Adversarial scenario types for XPIA Jailbreak"""

    ADVERSARIAL_INDIRECT_JAILBREAK = "adv_xpia"


@experimental
class _UnstableAdversarialScenario(Enum):
    """Adversarial scenario types that we haven't published, but still want available for internal use
    Values listed here are subject to potential change, and/or migration to the main enum over time.
    """

    ECI = "adv_politics"
    ADVERSARIAL_IMAGE_GEN = "adv_image_gen"
    ADVERSARIAL_IMAGE_MULTIMODAL = "adv_image_understanding"
