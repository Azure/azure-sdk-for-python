---
name: cu-sdk-common-knowledge
description: Domain knowledge for Azure AI Content Understanding. Use this skill to answer questions about Content Understanding concepts, analyzers, field schemas, API operations, and SDK usage. Always consult official documentation before answering.
---

# Azure AI Content Understanding Domain Knowledge

This skill provides domain knowledge for Azure AI Content Understanding, a multimodal AI service that extracts semantic content from documents, video, audio, and image files.

> **[COPILOT GUIDANCE]:** Always consult the official documentation first before answering user questions. Use `fetch_webpage` to read the relevant doc page when the reference material below is insufficient or may be outdated.
>
> When a user's question is broad or ambiguous, ask them to clarify:
> - "Which modality are you working with — documents, images, audio, or video?"
> - "Are you using a prebuilt analyzer, or building a custom one?"
> - "Are you asking about the Python SDK specifically, or the service in general?"

## Official Documentation

The authoritative source for Content Understanding is: **https://learn.microsoft.com/azure/ai-services/content-understanding/**

Always read the relevant page (via `fetch_webpage`) before answering if the reference material below does not cover the topic.

### Key Documentation Pages

| Topic | URL |
|-------|-----|
| **Overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/overview |
| **What's new** | https://learn.microsoft.com/azure/ai-services/content-understanding/whats-new |
| **Content Understanding Studio** | https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio?tabs=portal%2Ccu-studio |
| **Service limits** | https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits |
| **Region & language support** | https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support |
| **Prebuilt analyzers** | https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers |
| **Create custom analyzer** | https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/create-custom-analyzer?tabs=portal%2Cdocument&pivots=programming-language-rest |
| **Document markdown** | https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown |
| **Document elements** | https://learn.microsoft.com/azure/ai-services/content-understanding/document/elements |
| **Video overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/video/overview |
| **Video elements** | https://learn.microsoft.com/azure/ai-services/content-understanding/video/elements |
| **Audio overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/audio/overview |
| **Image overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/image/overview |
| **REST API reference** | https://learn.microsoft.com/rest/api/contentunderstanding/operation-groups |

> **Search tip:** If the above pages don't cover the user's question, search the doc tree at `https://learn.microsoft.com/azure/ai-services/content-understanding/`.

## Related Skills

- `cu-sdk-setup` — Set up Python environment and run samples
- `cu-sdk-sample-run` — Run specific samples interactively
