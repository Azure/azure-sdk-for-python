# This is the latest (June20,2024) code from AI Studio playground for Completions, it should fail against the latest package.

# NOT for final merge, only for testing purposes.
def failing_completions_studio_viewcode() -> None:
    import os
    import openai
    openai.api_type = "azure"
    openai.api_base = os.environ["AZURE_OPENAI_ENDPOINT"]
    openai.api_version = "2024-02-01"
    openai.api_key = os.environ["AZURE_OPENAI_KEY"]

    response = openai.Completion.create(
    engine= os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
    prompt="hello world",
    temperature=1,
    max_tokens=100,
    top_p=0.5,
    frequency_penalty=0,
    presence_penalty=0,
    best_of=1,
    stop=None)


if __name__ == "__main__":
    failing_completions_studio_viewcode()