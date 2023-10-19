# incremental_many_docs

A set of folders which contain documents that are added or modified with each subsequently named `*_run`.
This enables testing the incremental update logic (tracking of changed documents, chunks derived from them, and deletions of documents and chunks) which EmbeddingsContainer implements.

## `first_run`

Various documents of different types are present in their 'original' form.

## `second_run`

- `office_docs/Azure CoPilot (AKS) Question.xlsx`: Questions near the end of the doc from `Resource Management` topic have been removed.
- `pdfs/nrl-llm-talk-pdf.pdf`: Document is new.
- `plain_text/CommiteSupportProgramsGRH.txt`: Document has been deleted.
- `plain_text/tutorials_suffix.md`: Document has been deleted.
- `plain_text/baby_shark_draft.md`: Document is new.
- `plain_text/in_progress/baby_shark_draft.md`: Document is ne, and important different in content than `plain_text/baby_shark_draft.md`
- `plain_text/BicycleBicycleBicycle.md`: Document has been renamed from `plain_text/BicycleBicycle.md`.
    - Renames are no handled for reuse as of 2023-09-15
