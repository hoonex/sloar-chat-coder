# First Run Guide

This guide is for someone who has never used Sloar and may not know which AI coding integrations are required.

## The shortest path

1. Get a local copy of this repository.
2. Run `install.py --target <your-project>`.
3. Open the target project in your preferred AI coding surface.
4. Ask the agent to run the Sloar first-run capability check.
5. Let Sloar choose the lowest sufficient capability path.

No GitHub plugin is required for the local engineering loop. A connected GitHub app is useful when you want the chat surface itself to read/write repositories, branches, PRs, CI logs, or artifacts.

## ChatGPT setup

### Understand the layers

ChatGPT's current workflow model separates three concepts:

- **Plugin** — a discoverable workflow package. A plugin can include skills and can depend on apps.
- **App** — an authenticated connection to an external service or action surface.
- **Skill** — reusable workflow instructions.

Sloar core is a **Skill**. GitHub access is provided by the **GitHub App** when that app is available and connected. A future Sloar Plugin can make discovery/setup easier, but the repository skill works without such a listing.

### Connect GitHub when you want repository integration

In supported ChatGPT experiences:

1. Open the Plugin directory or `Settings -> Plugins`.
2. Find the GitHub capability/plugin and inspect the included app requirements.
3. Select Connect when available and finish OAuth.
4. On GitHub, grant access only to repositories you intend ChatGPT to use.
5. Return to ChatGPT and verify the repository appears. Newly granted repositories can take a short time to surface.

Availability can vary by plan, workspace settings, role, supported surface, and region. A workspace admin may also disable an app. Therefore Sloar treats the visible tool inventory as evidence and never assumes GitHub read/write access exists.

Official product references at the time of Sloar 0.2.0:

- https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex
- https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

If the product UI changes later, follow the current official OpenAI help text rather than preserving these menu names by force.

## What the first-run check should report

The agent should produce a compact capability map only when useful:

```text
Surface: ChatGPT / Codex / other / unknown
Execution: available / unavailable
Repository read: available via ... / unavailable
Repository write: available via ... / unavailable
PR + CI inspection: available / unavailable
Web access: available / unavailable
Best starting level: L0..L5
Missing setup that actually blocks the requested task: ...
```

It must distinguish:

- **not installed** — a capability is known to exist but is absent;
- **not authorized** — integration exists but permission is missing;
- **not exposed on this surface** — the current client does not offer the capability;
- **not needed** — absence does not block the task.

Do not send a beginner through setup steps for capabilities the task does not need.

## If GitHub is not connected

Sloar should degrade gracefully:

- use the sandbox/local clone when available;
- accept an uploaded repository archive or bundle;
- produce a verified patch/diff instead of pretending it pushed;
- clearly identify publication as the only blocked stage when that is true.

## If there is no terminal or sandbox

Sloar can still improve planning and evidence discipline, but it cannot claim repository-wide verification without a code-execution environment. The correct state may be L5 for implementation while still providing exact setup instructions.

## Install details

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target ../my-project
```

Useful flags:

```text
--dry-run       show intended changes without writing
--no-agents     do not edit/create target AGENTS.md
--force         replace an existing Sloar skill directory
```

The installer refuses to silently replace an existing different Sloar installation unless `--force` is supplied.

## Local doctor

```bash
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py .
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py . --json
```

`doctor.py` diagnoses the filesystem/terminal side only. It intentionally does not guess ChatGPT account/plugin state.

## First prompt examples

See [../examples/first-prompt.md](../examples/first-prompt.md).
