# ChatGPT connection recommendations

Sloar does not require a specific ChatGPT Plugin/App to perform local repository engineering. A local Git worktree plus code execution is enough for the core protocol.

External connections become useful when the user wants ChatGPT/Codex to operate remote services directly. Sloar recommends them from durable repository signals, but **the user connects them manually** and the agent must verify the capabilities actually exposed in the current session.

## Connection levels

### Baseline for a full remote workflow

**GitHub** — recommended when the repository origin is GitHub and the user wants the agent to read/write remote files, work with branches and pull requests, inspect Actions/CI, or publish through GitHub.

GitHub is not required for local-only Sloar usage. Grant access only to repositories the user intends the agent to operate. A successful read does not prove write, PR, Actions, or workflow-file permission; Sloar verifies required capabilities separately.

### Repository-specific recommendations

Sloar's First Run Wizard looks for these signals and recommends the corresponding connection only when relevant:

| Connection | Repository signal | Why connect it |
| --- | --- | --- |
| Vercel | `vercel.json`, `.vercel/project.json`, Vercel package metadata | Inspect/deploy projects and production state |
| Supabase | `supabase/`, Supabase SDK/dependency metadata | Database, Auth, migrations, Edge Functions, project state |
| Netlify | `netlify.toml`, `.netlify/`, Netlify package metadata | Build/deploy/project operations |
| OpenAI Platform | OpenAI SDK/dependency metadata | API keys, project configuration, OpenAI-backed runtime setup |

These are recommendations, not proof that the provider is used in production and not proof that the ChatGPT connection is available on the current plan/workspace/surface.

## User-controlled connection flow

1. Run `python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .`.
2. Review `Suggested connections` or the `connections.items` array in `--json` output.
3. In ChatGPT/Codex, open the current Plugins/Apps/Connections interface and search for the provider by name.
4. Choose **Connect** and authenticate directly with that provider.
5. Grant the smallest repository/project scope that supports the intended task.
6. Return to the coding conversation and let the agent verify actual read/write/PR/CI/deploy capabilities before relying on them.

Sloar never asks the user to paste provider passwords, access tokens, service-role keys, or API secrets into the conversation merely to establish a connection.

## Required vs recommended

- **Core Sloar:** no external ChatGPT connection is mandatory.
- **GitHub remote workflow:** GitHub connection is the baseline connection.
- **Deployment/database/provider operations:** connect only the provider actually detected/needed for the task.
- **Missing connection:** continue local IMPLEMENT/VERIFY when possible; do not incorrectly classify missing setup as a platform outage.

## Permission mismatches

Connections can be partial. For example, a GitHub App may be able to write normal repository files but be denied when updating `.github/workflows/*` because a narrower workflows permission is missing.

Sloar classifies these as `REMOTE_PARTIAL`, not `REMOTE_DEGRADED`, and changes strategy instead of retrying the same forbidden operation.
