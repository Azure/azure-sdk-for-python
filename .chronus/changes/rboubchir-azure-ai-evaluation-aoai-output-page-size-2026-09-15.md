---
changeKind: feature
packages:
  - azure-ai-evaluation
---

Added the `aoai_output_items_page_size` option to `evaluate` for configuring the number of native Azure OpenAI
grader output items requested per HTTP response page. The default remains 100, and all result pages are fetched.
