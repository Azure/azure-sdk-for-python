# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mock implementation of AttackObjective for testing."""

from typing import Any, Dict, List, Optional
from azure.ai.evaluation._common._experimental import experimental


@experimental
class MockMessage:
    """Mock implementation of Message for testing.
    
    :param role: The role in the conversation (e.g., 'user', 'assistant')
    :type role: str
    :param content: The content of the message
    :type content: str
    """

    def __init__(self, role: Optional[str] = None, content: Optional[str] = None) -> None:
        self.role = role
        self.content = content

    def __repr__(self) -> str:
        return f"MockMessage(role='{self.role}', content='{self.content}')"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert the message to a dictionary.
        
        :return: Dictionary representation of the message
        :rtype: Dict[str, Optional[str]]
        """
        return {
            "Role": self.role,
            "Content": self.content
        }


@experimental
class MockTargetHarm:
    """Mock implementation of TargetHarm for testing.
    
    :param risk_type: The risk type (e.g., 'violence', 'hate')
    :type risk_type: str
    :param risk_sub_type: The risk subtype
    :type risk_sub_type: str
    """

    def __init__(self, risk_type: Optional[str] = None, risk_sub_type: Optional[str] = None) -> None:
        self.risk_type = risk_type
        self.risk_sub_type = risk_sub_type

    def __repr__(self) -> str:
        return f"MockTargetHarm(risk_type='{self.risk_type}', risk_sub_type='{self.risk_sub_type}')"

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert the target harm to a dictionary.
        
        :return: Dictionary representation of the target harm
        :rtype: Dict[str, Optional[str]]
        """
        return {
            "RiskType": self.risk_type,
            "RiskSubType": self.risk_sub_type
        }


@experimental
class MockMetadata:
    """Mock implementation of Metadata for testing.
    
    :param target_harms: List of target harms
    :type target_harms: List[MockTargetHarm]
    :param language: The language of the attack objective
    :type language: str
    """

    def __init__(self, target_harms: List[MockTargetHarm], language: str) -> None:
        self.target_harms = target_harms
        self.language = language

    def __repr__(self) -> str:
        return f"MockMetadata(target_harms={self.target_harms}, language='{self.language}')"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary.
        
        :return: Dictionary representation of the metadata
        :rtype: Dict[str, Any]
        """
        return {
            "TargetHarms": [harm.to_dict() for harm in self.target_harms],
            "Language": self.language
        }


@experimental
class MockAttackObjective:
    """Mock implementation of AttackObjective for testing.
    
    :param source: List of sources
    :type source: List[str]
    :param modality: The modality of the attack objective
    :type modality: str
    :param messages: The messages in the attack objective
    :type messages: List[MockMessage]
    :param metadata: The metadata of the attack objective
    :type metadata: Optional[MockMetadata]
    """

    def __init__(
        self,
        source: List[str],
        modality: str,
        messages: List[MockMessage],
        metadata: Optional[MockMetadata] = None
    ) -> None:
        self.source = source
        self.modality = modality
        self.messages = messages
        self.metadata = metadata

    def __repr__(self) -> str:
        return f"MockAttackObjective(source={self.source}, modality='{self.modality}', messages={self.messages}, metadata={self.metadata})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the attack objective to a dictionary.
        
        :return: Dictionary representation of the attack objective
        :rtype: Dict[str, Any]
        """
        result = {
            "Source": self.source,
            "Modality": self.modality,
            "Messages": [message.to_dict() for message in self.messages]
        }
        
        if self.metadata:
            result["Metadata"] = self.metadata.to_dict()
        
        return result

    @classmethod
    def create_mock_objectives(cls, risk_category: Optional[str], count: int = 5) -> List["MockAttackObjective"]:
        """Create a list of mock attack objectives.
        
        :param risk_category: List of risk categories to include
        :type risk_category: Optional[str]
        :param count: Number of mock objectives to create
        :type count: int
        :return: List of mock attack objectives
        :rtype: List[MockAttackObjective]
        """
        result = []
        
        for i in range(count):
            # Create mock metadata with target harms
            target_harms = [MockTargetHarm(risk_type=risk_category, risk_sub_type="")]
            metadata = MockMetadata(target_harms=target_harms, language="en")
            risk_type = risk_categories[risk_idx]
            
            # Create mock metadata with target harms
            target_harms = [MockTargetHarm(risk_type=risk_category, risk_sub_type="general")]
            metadata = MockMetadata(target_harms=target_harms, language="en")
            risk_type = risk_category
            
            # Create mock message
            messages = [MockMessage(role="user", content=f"Mock attack prompt for {risk_type} #{i+1}")]
            
            # Create mock attack objective
            objective = cls(
                source=["mock_source"],
                modality="text",
                messages=messages,
                metadata=metadata
            )
            
            result.append(objective)
            
        return result

    @classmethod
    def create_mock_response(cls, risk_categories: List[str], count: int = 5) -> Dict[str, Any]:
        """Create a mock response for get_attack_objectives.
        
        :param risk_categories: List of risk categories to include
        :type risk_categories: List[str]
        :param count: Number of mock objectives to create
        :type count: int
        :return: Mock response dictionary
        :rtype: Dict[str, Any]
        """
        objectives = cls.create_mock_objectives(risk_categories, count)
        
        # Format response as expected by the _red_team_agent.py
        formatted_objectives = []
        
        for obj in objectives:
            # Extract message content
            content = obj.messages[0].content if obj.messages else ""
            risk_type = obj.metadata.target_harms[0].risk_type if obj.metadata and obj.metadata.target_harms else ""
            
            formatted_objectives.append({
                "risk_category": risk_type,
                "conversation_starter": content,
                "metadata": {
                    "category": {
                        "risk-type": risk_type
                    }
                },
                "messages": [
                    {"content": content}
                ]
            })
            
        return {"objectives": formatted_objectives}