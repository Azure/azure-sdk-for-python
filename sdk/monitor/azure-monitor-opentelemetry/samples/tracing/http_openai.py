from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# The HTTPX instrumentation captures http requests made in the OpenAI library.
# For openai>=1.4.0, it is important to instrument httpx before importing openai.
HTTPXClientInstrumentor().instrument()

# import openai # For openai==0.x
from openai import OpenAI # For openai==1.x
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

# The OpenAI Instrumation is not officially part of the OpenTelemetry community.
# Therefore, we cannot atest to its stability. Use with appropiate caution to capture additional telemetry.
OpenAIInstrumentor().instrument()

client = OpenAI() # For openai==1.x
completion = client.chat.completions.create( # For openai==1.x
# completion = openai.ChatCompletion.create( # For openai==0.x
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)
print(completion.choices[0].message)

input()