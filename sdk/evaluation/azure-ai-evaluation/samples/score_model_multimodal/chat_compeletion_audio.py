import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def demonstrate_score_model_grader():
    endpoint = os.getenv("endpoint", "")
    deployment = os.getenv("deployment_name_audio", "gpt-4o-audio-preview")
    subscription_key = os.getenv("api_key", "")

    # Initialize Azure OpenAI client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2025-01-01-preview",
    )

    AUDIO_FILE_PATH = os.getcwd() + "/samples/score_model_multimodal/input_audio.wav"
    with open(AUDIO_FILE_PATH, "rb") as audio_file:
        encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

    # Prepare the chat prompt
    chat_prompt = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "You are an AI assistant that helps people find information."},
                {"type": "input_audio", "input_audio": {"data": encoded_audio, "format": "wav"}},
            ],
        }
    ]

    # Include speech result if speech is enabled
    messages = chat_prompt

    # Generate the completion
    completion = client.chat.completions.create(
        model=deployment, modalities=["text", "audio"], audio={"voice": "alloy", "format": "wav"}, messages=messages
    )

    print(completion.to_json())


if __name__ == "__main__":
    print("🚀 Starting Chat Completion Audio Demo\n")

    # Check if environment variables are set
    required_vars = ["endpoint", "api_key", "deployment_name_audio"]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
    else:
        print("✅ All environment variables found")
        demonstrate_score_model_grader()

    print("\n🎉 Demo completed!")
