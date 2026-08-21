# Environment onboarding

ONBOARD is a lightweight pre-state used when the user or the current session may not know which capabilities are actually available. It exists to help first-time users without turning every task into setup ceremony.

## Entry conditions

Run ONBOARD when one or more are true:

- the user explicitly asks how to set up or start Sloar;
- this is the first repository task and tool/capability availability is unknown;
- the requested task requires a capability whose authorization/exposure is uncertain;
- an earlier session relied on tools that are not visible in the current session.

Skip or compress ONBOARD when capabilities are already evidenced in the current session.

## Capability map

Classify only capabilities relevant to the requested task:

```text
surface
execution
repository_read
repository_write
branch_pr
ci_logs_artifacts
web
remote_execution
artifact_transport
```

Each capability should carry both state and evidence source. Useful states:

```text
available
unavailable
unknown
not_needed
not_authorized
not_exposed
```

Do not infer `available` from product marketing, prior sessions, or a plugin name alone.

## ChatGPT plugin/app/skill rule

When the current product surface is ChatGPT or Codex and setup guidance is needed:

1. Treat a **Plugin** as a workflow package that can contain skills and depend on apps.
2. Treat an **App** as the authenticated external data/action connection.
3. Treat a **Skill** as reusable instructions/workflow guidance.
4. Sloar core is a skill. A GitHub app connection is separate authorization and is not implied by Sloar installation.
5. If GitHub capability is needed but missing, explain the current official Plugin/App connection path only if the surface actually supports it.
6. If equivalent repository capabilities already exist, do not send the user through redundant plugin setup.
7. If availability is plan/workspace/role/region dependent, say so instead of treating a missing button as user error.

Product UI changes over time. Prefer current official product documentation over stale hard-coded menu paths when web lookup is available.

## Connection recommendations

Sloar should help the user decide **which external connections are worth enabling**, but it must not connect providers silently or claim they are connected merely because the repository contains provider files.

Core Sloar does not require an external ChatGPT Plugin/App when exact local Git plus code execution is available. For a full hosted workflow, recommend connections from repository evidence and requested operations:

- **GitHub** — baseline connection when the origin is GitHub and the user wants ChatGPT/Codex to operate remote branches, PRs, CI, or publication.
- **Vercel** — recommend only when Vercel repository signals exist and deployment/project operations matter.
- **Supabase** — recommend only when Supabase repository signals exist and DB/Auth/Edge Function/project operations matter.
- **Netlify** — recommend only when Netlify repository signals exist and deployment/project operations matter.
- **OpenAI Platform** — recommend when OpenAI SDK/dependency signals exist and the task needs API-key/project/runtime configuration.

`scripts/wizard.py` detects these repository signals and emits `connections.items`. Detection always leaves connection `status` as `unknown`; the user connects the provider explicitly, then the agent verifies the actual tools/permissions exposed in the current session.

When presenting connection guidance to a user:

1. distinguish **baseline for the requested remote workflow** from merely **recommended**;
2. explain why the repository triggered the recommendation;
3. tell the user to connect the provider themselves through the current Plugins/Apps/Connections UI;
4. recommend least-privilege repository/project scope;
5. never request passwords, access tokens, service-role keys, or API secrets merely to establish the ChatGPT connection;
6. after connection, verify read/write/PR/CI/deploy capabilities individually instead of assuming all permissions came with the connection.

Read `docs/CONNECTIONS.md` or `docs/CONNECTIONS.ko.md` for the user-facing guide.

## Readiness capsule

When the user is new, default to a short status capsule rather than a capability dump:

```text
Sloar readiness
Repository: ready | missing | unknown
Execution: ready | missing | unknown
GitHub read/write: ready | partial | missing | unknown
CI/browser: ready | partial | missing | unknown
Suggested connections: provider list from repository evidence
Next: ready to work | one concrete setup action
```

The capsule is a view over evidence, not a replacement for the evidence ledger. `scripts/wizard.py` may provide the local half of this report. The agent must resolve the hosted half from the current session's actual tools/apps.

## Hosted capability resolution

Do not ask a beginner to identify implementation details such as connector names. The agent should inspect its own available capabilities and classify them. In ChatGPT/Codex, a visible GitHub-backed tool is evidence of exposure, but write permission must be proven by its declared capability or an authorized operation; read access does not imply write access.

A locally installed GitHub CLI is separate from a ChatGPT GitHub App connection. Likewise, installing a Plugin does not automatically grant every underlying App permission.

If the user asks for Plugin setup, prefer current official OpenAI documentation because product menus and availability change. Sloar itself is an Agent Skill repository and does not claim that installing the Skill automatically installs or authorizes any external App.

## First-run response contract

Keep the user-facing onboarding compact. Report:

- what is already usable;
- what is genuinely missing for the requested task;
- which connections are baseline/recommended for this repository and why;
- the lowest viable capability level;
- one concrete next action only when user action is required.

Do not dump the entire capability ladder unless it helps the user.

## No-setup dead ends

Missing hosted integrations are not automatically blockers.

Examples:

- GitHub write unavailable + local git available -> implement/verify locally and prepare exact publication artifact.
- GitHub read unavailable + user supplied complete archive -> materialize archive and continue.
- browser unavailable locally + CI browser job available -> L4 may be justified for that verification only.
- no execution environment -> implementation/verification claims are blocked even if repository text can be read.

## Exit condition

ONBOARD exits when:

1. the required task capabilities are evidenced or explicitly classified unavailable;
2. the lowest viable capability level is selected;
3. any user-owned setup blocker is stated concretely;
4. normal Sloar state begins at RECOVER or IDENTIFY.

ONBOARD does not itself authorize apps, grant repository permissions, or create remote state.
