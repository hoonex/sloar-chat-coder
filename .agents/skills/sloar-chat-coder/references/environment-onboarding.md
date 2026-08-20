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

## Readiness capsule

When the user is new, default to a short status capsule rather than a capability dump:

```text
Sloar readiness
Repository: ready | missing | unknown
Execution: ready | missing | unknown
GitHub read/write: ready | partial | missing | unknown
CI/browser: ready | partial | missing | unknown
Next: ready to work | one concrete setup action
```

The capsule is a view over evidence, not a replacement for the evidence ledger. `scripts/wizard.py` may provide the local half of this report. The agent must resolve the hosted half from the current session's actual tools/apps.

## Hosted capability resolution

Do not ask a beginner to identify implementation details such as connector names. The agent should inspect its own available capabilities and classify them. In ChatGPT/Codex, a visible GitHub-backed tool is evidence of exposure, but write permission must be proven by its declared capability or an authorized operation; read access does not imply write access.

A locally installed GitHub CLI is separate from a ChatGPT GitHub App connection. Likewise, installing a Plugin does not automatically grant every underlying App permission.

If the user asks for Plugin setup, prefer current official OpenAI documentation because product menus and availability change. As of Sloar 0.3.0, the Plugin Directory is the primary discovery surface across ChatGPT and Codex, plugins may package skills/apps/app templates, and underlying Apps retain their own authentication and permissions. Sloar itself is not claiming a Plugin Directory listing.

## First-run response contract

Keep the user-facing onboarding compact. Report:

- what is already usable;
- what is genuinely missing for the requested task;
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
