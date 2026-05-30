# Phase 4: Register 📋

> 📍 **Phase 4 — Register** | Add the skill to the find-package-skill discovery table.

## Step 1 — Update find-package-skill

Add a row to `.github/skills/find-package-skill/SKILL.md` in the **Package Skills** table:

```markdown
| `<package-name>` | `sdk/<service>/<package-name>/.github/skills/<package-name>/SKILL.md` |
```

Example:

```markdown
| `azure-ai-projects` | `sdk/ai/azure-ai-projects/.github/skills/azure-ai-projects/SKILL.md` |
```

## Step 2 — Summary

Print a summary of everything created:

📋 **Package Skill Created**

| Item | Path | Status |
|---|---|---|
| SKILL.md | `sdk/<service>/<package-name>/.github/skills/<package-name>/SKILL.md` | Created |
| architecture.md | `...references/architecture.md` | Created/Skipped |
| customizations.md | `...references/customizations.md` | Created/Skipped |
| find-package-skill | `.github/skills/find-package-skill/SKILL.md` | Updated |
| vally lint | 3/3 checks | Passed |

**Next steps for the service team:**
1. Fill in any `<!-- TODO -->` sections with domain-specific knowledge.
2. Test the skill by asking an agent to regenerate your package (`azsdk_package_generate_code`) and apply a small TypeSpec change — the agent should consult the skill, not guess.
3. Iterate: agent gets something wrong → update skill → test again.
4. Submit a PR.

**Maintaining your skill:**
- When your package's `_patch.py` files or utility modules change, update the skill.
- Keep content static — no version numbers, no current API version values, no release-specific info. Point to source files for things that change.
- When adding a new sync customization, make sure the skill reminds the agent about the async counterpart under `aio/`.

## Step 3 — CONFIRM

Question: "Register the skill in find-package-skill now (recommended), or skip?"

📍 **Phase 4 complete** | Skill registered | Wizard done 🎉
