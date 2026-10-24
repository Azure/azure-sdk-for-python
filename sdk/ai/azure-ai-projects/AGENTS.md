# azure-ai-projects agent workflows

These instructions apply only to `sdk/ai/azure-ai-projects`.

For TypeSpec regeneration in a GitHub Copilot cloud-agent session, read and follow
[the cloud regeneration skill](.github/skills/azure-ai-projects-cloud-regeneration/SKILL.md)
before installing generation dependencies. It runs the package's pinned tools and
validation on a dedicated Actions runner, then returns a package-only patch.
Do not use the interactive local emission skill in a cloud session.

For local emission, use
[the existing emission skill](.github/skills/azure-ai-projects-emit-from-typespec/SKILL.md).
Other package-specific skills are listed in [.github/skills/README.md](.github/skills/README.md).

A feed DNS failure is an environment blocker, not permission to replace approved
feeds, disable the firewall, omit the pinned wheel, or claim generation succeeded.
