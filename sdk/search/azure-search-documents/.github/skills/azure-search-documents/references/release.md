# azure-search-documents - Release and Branching

## Release tracks

Choose the release track before comparing APIs or writing changelog entries:

| Release track | Branch source | Branch name |
| --- | --- | --- |
| Preview | Start from `main`, which includes the latest preview API surface. | `search/<api-version>`, for example `search/2026-05-01-preview` |
| GA | Start from the previous GA branch, not from the latest preview. | `search/<api-version>-ga`, for example `search/2026-05-01-ga` |

## Branch-dependent API surface

Do not assume the latest preview API exists on a GA branch. Method names, resource types, generated models, helper accessors, and package-specific kwargs can differ between branches.

Use method and kwarg inventories in this skill and `customizations.md` as pattern checklists, not as the current branch's source of truth. Before adding, removing, or forwarding a wrapper, verify the current branch's generated operations and `_patch.py` methods. If an example method, accessor, or kwarg does not exist on the current branch, do not add it just to satisfy the checklist.

If the current branch differs from the inventories in many places, consider regenerating the package skill using `.github\skills\create-package-skill\SKILL.md` instead of patching entries one by one.

## CHANGELOG conventions

### Drafting changelog entries

1. Start from the spec PR's `CHANGELOG.md`. Map its sections to ours and use it as the candidate list of what changed.
2. Treat generated SDK code as the source of truth. Confirm each candidate entry exists in the current generated code with `venv python -c "from ... import X; print(X)"`.
3. Group entries by symbol kind and feature theme when meaningful. Kinds are `clients`, `enum members`, `models`, `operations`, `parameters`, `properties`; combine kinds inline when a group includes more than one kind.
4. Write each group as a lead-in bullet with an indented sublist. Use one of these patterns:
   - `Below <kinds> are added [or changed] [for <theme>]`
   - `Below <kinds> are renamed`
   - `Below <kinds> do not exist in this release`
5. Sort entries within each sublist alphabetically by fully qualified name.

### Checking whether a symbol exists in a release

- Spot-check: `git show azure-search-documents_<prev-version>:sdk/search/azure-search-documents/<path>`.
- Full dump: `pip install azure-search-documents==<prev-version>` into a temp venv, dump via `dir()` / `inspect.signature`, diff against current. Run from outside the package root or local source shadows the wheel.

### Preview releases

- `Features Added`: list changes since the previous preview release.
- `Breaking Changes`: list breaking changes since the previous preview release. Prepend this beta-only disclaimer:

```markdown
> These changes do not impact the API of stable versions such as <latest GA version>.
> Only code written against a beta version such as <latest beta version> may be affected.
```

### GA releases

- `Features Added`: list changes since the previous GA release. Do not compare against the latest preview.
- `Breaking Changes`: when both categories apply, group them in this order:
  1. Breaking changes since the previous GA release, with no disclaimer.
  2. Breaking changes since the latest preview in this GA's minor, prepended with this beta-only disclaimer:

```markdown
> These changes do not impact the API of stable versions such as <previous GA version>.
> Only code written against a beta version such as <latest beta of this GA's minor> may be affected.
```
