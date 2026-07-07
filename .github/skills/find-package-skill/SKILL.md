---
name: find-package-skill
description: '**UTILITY SKILL** — Must be consulted before making any changes to packages under sdk/. Discovers and loads package-specific domain knowledge that prevents common mistakes. WHEN: "add feature to package", "fix bug in package", "modify package code", "regenerate from typespec", "change client library".'
---

# Find Package Skill

Some SDK packages in this monorepo have **package-specific skills** — tribal
knowledge (architecture, data flows, type mappings, pitfalls) that prevents
common mistakes. Before modifying any SDK package, check whether a skill exists
for it using the steps below.

## How to Discover Package Skills

1. **Determine the package directory.** If you already know the file path you're
   modifying, extract the package directory from it (e.g., a file at
   `sdk/search/azure-search-documents/azure/search/documents/_search_client.py`
   belongs to the package at `sdk/search/azure-search-documents/`). If you only
   have a package name, search for a matching directory under `sdk/` (package
   directories are named after the distribution package name, e.g.,
   `azure-search-documents` → `sdk/search/azure-search-documents/`).

2. **Check for a `.github/skills/` directory** inside the package directory. For
   example, check whether `sdk/search/azure-search-documents/.github/skills/` exists.

3. **If it exists**, read every `SKILL.md` found under that directory. If a
   `references/` subdirectory exists next to a `SKILL.md`, read all files in it
   too for additional context.

4. **If no `.github/skills/` directory exists** for the package, no
   package-specific skill has been created yet — proceed normally.