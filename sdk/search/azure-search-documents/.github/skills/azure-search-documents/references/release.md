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

Use `azsdk_package_update_changelog_content` to draft entries, then review and adjust.

The generated SDK code is the source of truth for CHANGELOG content. If something exists in generated code, treat it as present. Fall back to the TypeSpec config in the spec PR only when the generated code is ambiguous.

After drafting the CHANGELOG, verify both directions:

1. Code to CHANGELOG: for every changed item in generated code, verify it is reflected in `CHANGELOG.md`.
2. CHANGELOG to code: for every item in `CHANGELOG.md`, verify it matches actual code.

Use the import checks in `SKILL.md` plus targeted `venv python -c "from ... import X; print(X)"` checks for individual symbols.

Sort lists within each CHANGELOG section alphabetically by fully qualified name.

### Preview releases

- `Features Added`: list changes since the previous preview release.
- `Breaking Changes`: list breaking changes since the previous preview release. Put this beta-only disclaimer before the list:

```markdown
> These changes do not impact the API of stable versions such as <latest GA version>.
> Only code written against a beta version such as <latest beta version> may be affected.
```

### GA releases

- `Features Added`: list changes since the previous GA release. Do not compare against the latest preview.
- `Breaking Changes`: when both categories apply, group them in this order:
  1. GA-to-GA breaking changes, with no disclaimer.
  2. Preview-to-GA breaking changes, after this beta-only disclaimer:

```markdown
> These changes do not impact the API of stable versions such as <previous GA version>.
> Only code written against a beta version such as <latest beta of this GA's minor> may be affected.
```
