# ChatGPT Plugins, Apps, and Sloar

This page exists because the words **Plugin**, **App**, and **Skill** are easy to mix up.

## The current model

Sloar treats Plugins/Apps/Skills as separate layers:

- **Skill**: reusable workflow instructions. Sloar core lives here.
- **App/connection**: authenticated access to an external provider such as GitHub, Vercel, or Supabase.
- **Plugin**: a workflow package that may bundle skills and depend on apps/connections.

Product UI and availability can change by plan, workspace policy, role, surface, and region. Prefer the current ChatGPT/Codex Plugins/Apps/Connections UI and current OpenAI product documentation over stale hard-coded menu names.

## Where Sloar fits

Sloar Chat Coder is currently distributed as an **Agent Skill repository**. It does not claim that installing the Skill automatically installs or authorizes any external App.

Therefore:

- installing Sloar does not authorize GitHub;
- connecting GitHub does not automatically install Sloar into a repository;
- GitHub read access does not prove write/PR/Actions/workflow-file access;
- a local `gh` login is separate from a ChatGPT GitHub connection;
- detecting `vercel.json` or `supabase/` does not prove those providers are connected to ChatGPT.

## Which connections should a user enable?

Run the First Run Wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

The Wizard now emits repository-aware `Suggested connections` and, in `--json`, a structured `connections.items` list.

Typical policy:

1. **Local-only Sloar** — no external ChatGPT connection is inherently required.
2. **GitHub remote workflow** — GitHub is the baseline connection when the origin is GitHub and the user wants remote repo/branch/PR/CI/publication operations.
3. **Vercel/Supabase/Netlify/OpenAI Platform** — recommended only when repository signals and the requested work make that provider relevant.
4. **User connects providers manually** — Sloar never silently authenticates or asks the user to paste provider passwords/tokens into the chat merely to create a connection.
5. **Agent verifies capabilities afterwards** — a connection may be partial. For example, ordinary GitHub file writes can work while workflow-file writes are denied.

See [CONNECTIONS.md](CONNECTIONS.md) for the complete recommendation matrix.

## Beginner decision tree

1. **I only want local coding with an agent/terminal.** Install the Sloar skill into the repository. No hosted provider App is inherently required.
2. **I want ChatGPT/Codex to operate GitHub directly.** Connect GitHub, grant only the repositories needed for the task, then let the agent verify actual read/write/PR/CI capabilities.
3. **My repo uses Vercel/Supabase/Netlify/OpenAI.** Connect only the provider(s) the Wizard recommends and the task actually needs.
4. **A connection is missing or partially authorized.** Continue local work where possible; do not misclassify missing setup as a platform outage.

## Future Sloar Plugin

The repository can later be packaged as part of a Plugin workflow, but the core rule remains: authenticated external actions stay behind explicit user-controlled App permissions, and Sloar verifies actual capabilities instead of assuming them.
