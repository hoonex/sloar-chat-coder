# ChatGPT Plugins, Apps, and Sloar

This page exists because the words **Plugin**, **App**, and **Skill** are easy to mix up.

## The current model

As of Sloar 0.3.0 (2026-08-20), OpenAI documents the Plugin Directory as the primary discovery surface for workflow capabilities across ChatGPT and Codex. A plugin can include skills, apps, and app templates. Apps remain the authenticated integrations that connect ChatGPT/Codex to external data and actions.

Official reference:

- https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex

Availability depends on plan, workspace policy, role, surface, region, and the capabilities of included apps. Always follow current OpenAI product documentation if UI labels change.

## Where Sloar fits

Sloar Chat Coder is currently distributed here as an **Agent Skill repository**. It is **not claiming to be a published Plugin Directory listing**.

- Sloar Skill: workflow/repository-engineering instructions.
- GitHub App/integration: authenticated repository data/actions when exposed to the current chat surface.
- Plugin: a discoverable package that may bundle a skill and one or more apps.

Therefore:

- installing Sloar does not authorize GitHub;
- connecting GitHub does not automatically install Sloar into a repository;
- GitHub read access does not prove GitHub write access;
- a local `gh` login is not the same thing as a ChatGPT GitHub App connection.

## Beginner decision tree

1. **I only want local coding with an agent/terminal.** Install the Sloar skill into the repository. No hosted GitHub app is inherently required.
2. **I want ChatGPT/Codex to read GitHub directly.** Use the current Plugin Directory/App connection flow when available, authorize only needed repositories, then ask the agent to verify repository read capability.
3. **I want it to push branches/PRs or inspect CI.** The agent must verify those actions are actually exposed and authorized. Do not infer write permission from a successful read.
4. **I do not see the relevant plugin/app.** This may be plan/workspace/role/surface/region policy. Use local/sandbox paths when they satisfy the task instead of treating setup as mandatory.

## Future Sloar Plugin

The repository is structured so Sloar can later be packaged as part of a Plugin workflow, but a future listing should not change the core rule: authenticated external actions stay behind explicit app permissions, and Sloar must inspect actual capabilities instead of assuming them.
