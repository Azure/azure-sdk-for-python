This is an SDK repo. Everything under `_generated/` is AutoRest output—never edit those files. Customizations live outside `_generated/`, and those are the only files we update.

### Task 1
- Diff each generated file between `HEAD~1` and `HEAD`, copy the added/removed imports into the matching customization file, and update its `__all__` tuple.
- Keep anything already marked complete unless the regeneration introduces new names on the next pass.
- Pairs to sync:
  - ✅ Generated `azure/search/documents/indexes/_generated/models/__init__.py` ↔ customized `azure/search/documents/indexes/models/__init__.py`
  - ✅ Generated `azure/search/documents/_generated/models/__init__.py` ↔ customized `azure/search/documents/models/__init__.py` *(no changes required)*
  - ✅ Generated `azure/search/documents/knowledgebase/_generated/models/__init__.py` ↔ customized `azure/search/documents/knowledgebase/models/__init__.py`

### Task 2
- Run `git diff HEAD~1 HEAD -- azure/search/documents/indexes/_generated/models/_models_py3.py` and keep that diff handy for reference. Repeat for `azure/search/documents/indexes/_generated/models/_index.py`.
- Walk the customization layers (`azure/search/documents/indexes/models/_models.py` and `azure/search/documents/indexes/models/_index.py`) top to bottom. For each class/enum/helper defined there, use the generated diff to decide whether new constructor args, defaults, validation maps, attribute maps, or helper method behavior needs to be **added** or **renamed**. Treat the customization types as the outer loop so nothing in the public surface is skipped.
- Mirror any newly generated members in the wrapper (constructor, maps, helpers), copy their docstrings **verbatim**, and update helpers/tests so every call site threads through the new or renamed members.
- When the generator renames something, adopt the new name and docstring; record removals for follow-up instead of deleting code on the spot.
- If the generated diff shows a brand-new type and we already maintain a customization wrapper for that type, sync the wrapper by adding any missing members/docstrings. If the type does not have a customization wrapper yet, do not create one—write it down as a follow-up decision so the feature team can weigh in.
- After finishing the sweep, rerun `git diff` on both customization files to confirm every generated change is reflected without losing custom logic.

### Task 3
- Diff the generated sync operations in `azure/search/documents/indexes/_generated/operations`. For every new or changed method, mirror the signature and docstrings in the matching customization clients: `azure/search/documents/indexes/_search_index_client.py` and `_search_indexer_client.py`.
- Repeat the same check under `azure/search/documents/indexes/_generated/aio/operations` and flow the updates into the async clients: `azure/search/documents/indexes/aio/_search_index_client.py` and `_search_indexer_client.py`.
- When new helpers land in the generated layer (for example, `knowledge_sources.get_status`), add matching wrappers in the custom clients (`get_knowledge_source_status`, etc.) so the public API stays in sync.
- Preserve any existing customization-specific behavior, but make sure the async/sync surfaces stay API-compatible with the generated layer.
