# User Coherence Evaluator

Evaluates whether simulated users in multi-turn agent conversations stay on topic or derail.

## How it works

- **Fetch** (`fetch_agent_conversations.py`): Connects to your Azure AI Foundry project, lists all conversations, identifies which agent each belongs to via `created_by.agent.name` on assistant messages, reverses messages to chronological order (the API returns newest-first), and saves per-agent JSON files.
- **Normalize** (`normalize_trace_messages`): Converts raw Foundry trace messages (which use `output_text`/`input_text` content types and include extra metadata) into simple `{"role": ..., "content": ...}` dicts.
- **Evaluate** (`UserCoherenceEvaluator`): For each conversation, pairs user/assistant messages into steps and sends them to an LLM in a single call. The LLM scores each user turn (0–2) on whether it's a natural follow-up to the preceding assistant response.
- **Results**: Per-step derail scores, per-conversation aggregate scores, and per-agent summary statistics.

## Setup

1. Install dependencies:

```bash
pip install azure-ai-projects azure-identity python-dotenv
```

2. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

3. Fetch conversations:

```bash
python fetch_agent_conversations.py
```

4. Open `user_coherence_evaluation.ipynb` and run all cells.
