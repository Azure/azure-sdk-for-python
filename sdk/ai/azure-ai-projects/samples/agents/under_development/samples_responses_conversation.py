from openai import OpenAI

client = OpenAI()


conversation = client.conversations.create()

response = client.responses.create(
    model="gpt-5-nano", input="Write a one-sentence bedtime story about a unicorn.", conversation=conversation.id
)

print(response.output_text)

# Continue the conversation
response = client.responses.create(model="gpt-5-nano", input="What happens next?", conversation=conversation.id)

print(response.output_text)

# List all messages in the conversation
items = client.conversations.items.list(conversation_id=conversation.id, limit=10)
print(items.data)
