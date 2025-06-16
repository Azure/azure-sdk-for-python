#!/usr/bin/env python3

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Sample demonstrating the use of AzureOpenAIScoreModelGrader for continuous
scoring evaluation.

This sample shows how to:
1. Configure an Azure OpenAI model for grading
2. Create a score model grader with custom prompts
3. Run evaluation using the evaluate() method
4. Interpret continuous scoring results

Prerequisites:
- Azure OpenAI resource with API key and endpoint
- Model deployment (e.g., gpt-4, gpt-4o-mini)
- Sample conversation data in JSONL format
- Environment variables configured in .env file
"""

import json
import os
from dotenv import load_dotenv
import pandas as pd
from azure.ai.evaluation import evaluate, AzureOpenAIScoreModelGrader
from azure.ai.evaluation import AzureOpenAIModelConfiguration

# Load environment variables
load_dotenv()


def create_sample_data() -> str:
    """Create sample conversation data for testing."""
    sample_conversations = [
        {
            "conversation": {
                "messages": [
                    {
                        "content": "How can I improve my Python coding skills?",
                        "role": "user"
                    },
                    {
                        "content": (
                            "Here are some effective ways to improve your "
                            "Python skills: 1) Practice coding daily with "
                            "platforms like LeetCode or HackerRank, 2) Work "
                            "on real projects that interest you, 3) Read "
                            "other people's code on GitHub, 4) Join Python "
                            "communities and forums, 5) Take online courses "
                            "or tutorials. The key is consistent practice and "
                            "building projects that challenge you."
                        ),
                        "role": "assistant"
                    }
                ]
            },
            "expected_quality": "high",
            "context": "Programming advice request"
        },
        {
            "conversation": {
                "messages": [
                    {
                        "content": "What is Python?",
                        "role": "user"
                    },
                    {
                        "content": "Python is a programming language.",
                        "role": "assistant"
                    }
                ]
            },
            "expected_quality": "low",
            "context": "Basic definition request"
        },
        {
            "conversation": {
                "messages": [
                    {
                        "content": (
                            "Can you explain machine learning concepts "
                            "for a beginner?"
                        ),
                        "role": "user"
                    },
                    {
                        "content": (
                            "Machine learning is a subset of artificial "
                            "intelligence where computers learn patterns from "
                            "data without being explicitly programmed. Think "
                            "of it like teaching a child to recognize animals "
                            "- you show them many pictures of cats and dogs, "
                            "and eventually they learn to distinguish between "
                            "them. In ML, we feed algorithms lots of data so "
                            "they can make predictions or decisions on new, "
                            "unseen data. Common types include supervised "
                            "learning (learning from labeled examples), "
                            "unsupervised learning (finding hidden patterns), "
                            "and reinforcement learning (learning through "
                            "trial and error)."
                        ),
                        "role": "assistant"
                    }
                ]
            },
            "expected_quality": "high",
            "context": "Educational explanation request"
        },
        {
            "conversation": {
                "messages": [
                    {
                        "content": "Help me debug this code",
                        "role": "user"
                    },
                    {
                        "content": "Sure, please share your code.",
                        "role": "assistant"
                    }
                ]
            },
            "expected_quality": "medium",
            "context": "Debug assistance request"
        },
        {
            "conversation": {
                "messages": [
                    {
                        "content": (
                            "What are the best practices for writing "
                            "clean Python code?"
                        ),
                        "role": "user"
                    },
                    {
                        "content": (
                            "Here are key best practices for writing clean "
                            "Python code: 1) Follow PEP 8 style guidelines "
                            "for consistent formatting, 2) Use descriptive "
                            "variable and function names that explain their "
                            "purpose, 3) Write docstrings for functions and "
                            "classes, 4) Keep functions small and focused on "
                            "a single task, 5) Use type hints to improve code "
                            "clarity, 6) Handle exceptions appropriately, "
                            "7) Write unit tests for your code, 8) Use "
                            "virtual environments for dependency management, "
                            "9) Comment complex logic but avoid obvious "
                            "comments, 10) Refactor code regularly to improve "
                            "readability and maintainability."
                        ),
                        "role": "assistant"
                    }
                ]
            },
            "expected_quality": "high",
            "context": "Best practices inquiry"
        }
    ]

    # Create JSONL file
    filename = "sample_conversations.jsonl"
    with open(filename, 'w') as f:
        for conv in sample_conversations:
            f.write(json.dumps(conv) + '\n')

    print(f"Created sample data file: {filename}")
    return filename


def demonstrate_score_model_grader():
    """Demonstrate the AzureOpenAIScoreModelGrader usage with real credentials."""

    # Create sample data
    data_file = create_sample_data()

    print("=== Azure OpenAI Score Model Grader Demo ===\n")

    try:
        # 1. Configure Azure OpenAI model using environment variables
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint=os.environ.get("4o_mini_target_endpoint"),
            api_key=os.environ.get("4o_mini_target_endpoint_key"),
            azure_deployment=os.environ.get(
                "4o_mini_target_endpoint_deployment_name"
            ),
            api_version="2024-12-01-preview"
        )

        print("✅ Model configuration loaded successfully")

        # 2. Create conversation quality grader
        conversation_quality_grader = AzureOpenAIScoreModelGrader(
            model_config=model_config,
            name="Conversation Quality Assessment",
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert conversation quality evaluator. "
                        "Assess the quality of AI assistant responses based on "
                        "helpfulness, completeness, accuracy, and "
                        "appropriateness. Return a score between 0.0 (very "
                        "poor) and 1.0 (excellent)."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Evaluate this conversation:\n"
                        "Context: {{ item.context }}\n"
                        "Messages: {{ item.conversation }}\n\n"
                        "Provide a quality score from 0.0 to 1.0."
                    )
                }
            ],
            range=[0.0, 1.0],
            sampling_params={
                "temperature": 0.0
            }
        )

        print("✅ Conversation quality grader created successfully")

        # 3. Run evaluation with the score model grader
        print("\n🚀 Running evaluation with score model grader...")

        result = evaluate(
            data=data_file,
            evaluators={
                "conversation_quality": conversation_quality_grader
            }
        )

        # 4. Display results
        print("\n=== Evaluation Results ===")
        print(f"Total samples evaluated: {len(result['rows'])}")

        # Show metrics
        print("\n=== Metrics Summary ===")
        for metric_name, metric_value in result['metrics'].items():
            print(f"{metric_name}: {metric_value:.3f}")

        # Show detailed results
        print("\n=== Sample Results ===")
        df = pd.DataFrame(result['rows'])

        for i, row in df.head(3).iterrows():
            print(f"\nSample {i+1}:")
            print(f"  Context: {row.get('context', 'N/A')}")
            
            # Show grader results
            for col in df.columns:
                if col.startswith('outputs.'):
                    grader_name = col.split('.')[1]
                    if 'score' in col:
                        print(f"  {grader_name} Score: {row[col]:.3f}")
                    elif 'passed' in col:
                        print(f"  {grader_name} Passed: {row[col]}")

        print("\n✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {str(e)}")
        print("\nFalling back to demonstration mode...")
        demonstrate_configuration_only()

    # Clean up
    if os.path.exists(data_file):
        os.remove(data_file)
        print(f"\n🧹 Cleaned up temporary file: {data_file}")


def demonstrate_configuration_only():
    """Demonstrate grader configuration without running actual evaluation."""
    
    try:
        # Create sample data
        data_file = create_sample_data()
        
        print("📝 Testing grader configuration...")
        
        # Configure with placeholder values for testing
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint="https://test-endpoint.openai.azure.com/",
            api_key="test-key",
            azure_deployment="gpt-4o-mini",
            api_version="2024-12-01-preview"
        )

        # Create a simple grader to test
        test_grader = AzureOpenAIScoreModelGrader(
            model_config=model_config,
            name="Test Quality Grader",
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "You are a test evaluator."
                },
                {
                    "role": "user",
                    "content": "Rate this: {{ data.conversation }}"
                }
            ]
        )
        
        print("✅ Grader creation successful!")
        print(f"   - Grader ID: {test_grader.id}")
        print(f"   - Grader name: {test_grader._grader_config.name}")
        print(f"   - Grader model: {test_grader._grader_config.model}")
        print(f"   - Input messages: {len(test_grader._grader_config.input)}")
        
        print("\n🚧 Implementation Status:")
        print("   - Sample data created: ✅")
        print("   - AzureOpenAIScoreModelGrader class: ✅ (implemented)")
        print("   - Integration with evaluate(): ✅ (ready for testing)")
        print("\n📖 Ready for use!")
        print("   Configure with real API credentials to run evaluations")
        
        # Clean up
        if os.path.exists(data_file):
            os.remove(data_file)
        
    except Exception as e:
        print(f"❌ Error testing implementation: {e}")
        print("\n🚧 Implementation Status:")
        print("   - Sample data created: ✅")
        print("   - AzureOpenAIScoreModelGrader class: ❌ (error)")
        print("   - Integration with evaluate(): ❌ (needs fixing)")


def demonstrate_different_grader_types():
    """Show examples of different score model grader configurations."""

    print("\n=== Different Score Model Grader Examples ===\n")

    examples = [
        {
            "name": "Helpfulness Grader",
            "description": (
                "Evaluates how helpful the AI response is to the user"
            ),
            "config": {
                "name": "Helpfulness Assessment",
                "input": [
                    {
                        "role": "system",
                        "content": (
                            "Rate how helpful this AI response is in "
                            "addressing the user's needs."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            "User Question: {{ data.question }}\n"
                            "AI Response: {{ data.response }}\n\n"
                            "Helpfulness score (0.0-1.0):"
                        )
                    }
                ],
                "range": [0.0, 1.0],
                "pass_threshold": 0.6
            }
        },
        {
            "name": "Factual Accuracy Grader",
            "description": (
                "Checks factual accuracy against reference information"
            ),
            "config": {
                "name": "Factual Accuracy Check",
                "input": [
                    {
                        "role": "system",
                        "content": (
                            "You are a fact-checker. Compare the AI response "
                            "with reference information and rate accuracy."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            "Reference: {{ data.reference }}\n"
                            "AI Response: {{ data.response }}\n\n"
                            "Accuracy score (0.0-1.0):"
                        )
                    }
                ],
                "range": [0.0, 1.0],
                "pass_threshold": 0.8
            }
        },
        {
            "name": "Clarity Grader",
            "description": (
                "Evaluates how clear and understandable the response is"
            ),
            "config": {
                "name": "Response Clarity",
                "input": [
                    {
                        "role": "developer",
                        "content": (
                            "Evaluate the clarity and understandability "
                            "of this AI response."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            "Response: {{ data.response }}\n\n"
                            "Clarity score (0.0-1.0, where 1.0 is perfectly "
                            "clear):"
                        )
                    }
                ],
                "range": [0.0, 1.0],
                "pass_threshold": 0.7,
                "sampling_params": {
                    "temperature": 0.1,
                    "max_tokens": 150
                }
            }
        }
    ]

    for example in examples:
        print(f"🎯 {example['name']}")
        print(f"   Description: {example['description']}")
        print("   Configuration:")
        config = example['config']
        print(f"     - Name: {config['name']}")
        print(f"     - Input Messages: {len(config['input'])} messages")
        print(f"     - Range: {config['range']}")
        print(f"     - Pass Threshold: {config['pass_threshold']}")
        if 'sampling_params' in config:
            print(f"     - Sampling Params: {config['sampling_params']}")
        print()


if __name__ == "__main__":
    print("🚀 Starting Azure OpenAI Score Model Grader Demo\n")
    
    # Check if environment variables are set
    required_vars = [
        "4o_mini_target_endpoint",
        "4o_mini_target_endpoint_key", 
        "4o_mini_target_endpoint_deployment_name"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nRunning in demonstration mode...\n")
        demonstrate_configuration_only()
    else:
        print("✅ All environment variables found")
        demonstrate_score_model_grader()
    
    demonstrate_different_grader_types()
    
    print("\n🎉 Demo completed!")
