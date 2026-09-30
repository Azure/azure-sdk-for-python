# Phase 4: Finalize 📋

> 📍 **Phase 4 — Finalize** | Confirm the skill is in its discoverable location and summarize.

## Step 1 — Confirm discoverable location

Package skills are discovered automatically by `find-package-skill`, which looks
for a `.github/skills/` directory **inside the package directory**. There is no
central registry to update — placement *is* registration.

Verify the skill lives at:

```
sdk/<service>/<package-name>/.github/skills/<package-name>/SKILL.md
```

If it's there, it will be discovered for that package. No further wiring needed.

## Step 2 — Summary

Print a summary of everything created:

📋 **Package Skill Created**

| Item | Path | Status |
|---|---|---|
| SKILL.md | `sdk/<service>/<package-name>/.github/skills/<package-name>/SKILL.md` | Created |
| architecture.md | `...references/architecture.md` | Created/Skipped |
| customizations.md | `...references/customizations.md` | Created/Skipped |
| find-package-skill | discovers automatically via package `.github/skills/` | No action |
| vally lint | 3/3 checks | Passed |

**Next steps for the service team:**
1. Fill in any `<!-- TODO -->` sections with domain-specific knowledge.
2. Test the skill by asking an agent to regenerate your package
3. Iterate: agent gets something wrong → update skill → test again.
4. Submit a PR.

**Maintaining your skill:**
- When your package's customizations change, update the skill.
- Keep content static — no version numbers or release-specific info

## Step 3 — CONFIRM

Question: "The skill is in place and will be discovered automatically. Anything else to adjust?"

📍 **Phase 4 complete** | Skill in place and discoverable | Wizard done 🎉
