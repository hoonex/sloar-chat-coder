# Sloar Chat Coder

Reliable repository engineering across disposable AI coding sessions.

Sloar Chat Coder is an Agent Skill for coding from chat surfaces where the execution sandbox can disappear, repository state can move concurrently, and connected tools may fail in ways that tempt an agent into guessing or retry loops.

Its goal is simple: **make repository work recoverable, exact, and evidence-bounded — even for a first-time user who has never configured an AI coding workspace before.**

> Durable truth over conversation memory. Evidence before completion claims.

## Start here

You do **not** need to understand Sloar's state machine before using it.

### 1. Get Sloar and install it

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

A downloaded ZIP works too; extract it and run the same installer from the extracted directory.

The installer copies the skill into `.agents/skills/sloar-chat-coder/` and adds an idempotent Sloar entry block to the target repository's `AGENTS.md`. It does not overwrite unrelated repository guidance.

Preview first with `--dry-run` when desired.

### 2. Run the First Run Wizard

Inside the target repository:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

The default output is deliberately short. It checks the local repository/execution side and marks ChatGPT/Codex GitHub, CI, browser, Plugin/App state as `unknown` until the agent verifies its actual current tools. Use `--json` for the full readiness report.

### 3. Tell your coding agent to use Sloar

A minimal first prompt is:

```text
Use Sloar Chat Coder for this repository. Run the first-run capability check before modifying anything, then recover the exact repository state and continue the task.
```

Read [docs/FIRST_RUN.md](docs/FIRST_RUN.md) for the full beginner path or [README.ko.md](README.ko.md) for Korean.

## New in 0.4: Forge resilience

Git is not the same failure domain as GitHub/GitLab/Actions. Sloar 0.4 keeps exact local engineering moving when a hosted layer is unavailable **and** distinguishes a real platform outage from an operation-specific permission/policy failure.

```text
LOCAL_READY + REMOTE_DEGRADED
  -> keep IMPLEMENT/VERIFY local
  -> defer remote publication

LOCAL_READY + REMOTE_PARTIAL
  -> preserve the verified tree
  -> change capability / identity / approval / policy path
  -> do not retry the same forbidden operation
```

### Check forge health

Network-free local state:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

One bounded remote probe, no automatic retries:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

### Classify a failure you already observed

No network request is made:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

Examples it distinguishes:

- GitHub App can write repository files but cannot update workflow files → `CAPABILITY_MISMATCH / REMOTE_PARTIAL`
- CI requires approval or returns `action_required` → `REMOTE_ACTION_REQUIRED / REMOTE_PARTIAL`
- branch ruleset/protection rejection → `POLICY_BLOCKED / REMOTE_PARTIAL`
- non-fast-forward/stale lease → `REMOTE_MOVED`, re-resolve and reconcile
- 429/5xx/DNS/timeout → `REMOTE_DEGRADED`

The classifier returns a normalized failure class, layer, retry strategy, next action, and SHA-256 fingerprint. It does not echo the raw failure text.

See [docs/FORGE_RESILIENCE.md](docs/FORGE_RESILIENCE.md) for the practical guide.

## ChatGPT: Plugin, App, and Skill are different things

Modern ChatGPT exposes workflow capabilities through **Plugins**. A plugin can package one or more **Skills** and can depend on **Apps**. Apps are integrations that authenticate to external systems and provide data/actions such as repository access.

For Sloar this means:

- **Sloar Skill**: the repository-engineering instructions in this project.
- **GitHub App**: the authenticated connection that may give ChatGPT repository read/write capabilities.
- **Plugin**: a discoverable workflow package that can bundle skills and apps. Sloar core does not require a future Sloar Plugin listing to function.

Installing Sloar never implies that GitHub is connected or that every GitHub operation is authorized. Sloar resolves the actual current capability instead of guessing from another session or from a successful read-only operation.

See [docs/FIRST_RUN.md](docs/FIRST_RUN.md#chatgpt-setup) and [docs/CHATGPT_PLUGINS.md](docs/CHATGPT_PLUGINS.md). Sloar is currently distributed as an Agent Skill repository, not as a claimed Plugin Directory listing.

## Why Sloar exists

Chat-based coding has a different failure model from a normal workstation:

- a sandbox can be recreated or lost;
- a branch may move while the agent is working;
- a connected repository write path can serialize content incorrectly or partially fail;
- a token/App can have repository-write permission but still lack one narrower capability;
- network access may exist in CI but not in the sandbox, or the reverse;
- a failed test can be a product regression, an external dependency failure, a policy gate, or a transport problem;
- long conversations can compress or lose working context.

Sloar treats those as engineering constraints rather than exceptions.

## The model

Every repository task moves through an explicit lifecycle:

```text
RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

Before that lifecycle begins, a first-time environment may run a lightweight **ONBOARD** capability check.

Publication is guarded by five concepts:

- **Repository identity** — commit SHA + tree SHA + working-tree state.
- **Capability ladder** — use the lowest sufficient execution/transport level.
- **Forge overlay** — distinguish `REMOTE_HEALTHY`, `REMOTE_PARTIAL`, and `REMOTE_DEGRADED`.
- **Failure fingerprint** — same failure + same inputs means change strategy, not blind retry.
- **Evidence ledger** — no verification evidence means no completion claim.

## Core invariants

1. Durable repository state outranks reconstructed conversation memory.
2. Establish exact repository identity before modification.
3. Prefer the sandbox work container over remote execution.
4. Use the lowest sufficient capability level.
5. Diagnose a failure before retrying or changing source.
6. Completion claims are bounded by collected evidence.
7. Revalidate mutable remote state immediately before publication.
8. Missing setup or one missing permission must not be confused with a platform outage.

## Repository layout

```text
.
├── AGENTS.md
├── README.md
├── README.ko.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── VERSION
├── docs/
│   ├── FIRST_RUN.md
│   ├── FIRST_RUN.ko.md
│   ├── CHATGPT_PLUGINS.md
│   ├── CHATGPT_PLUGINS.ko.md
│   ├── FORGE_RESILIENCE.md
│   └── FORGE_RESILIENCE.ko.md
└── .agents/skills/sloar-chat-coder/
    ├── SKILL.md
    ├── references/
    │   ├── capability-ladder.md
    │   ├── concurrency.md
    │   ├── evidence-ledger.md
    │   ├── forge-resilience.md
    │   ├── recovery.md
    │   ├── state-machine.md
    │   └── verification.md
    └── scripts/
        ├── doctor.py
        ├── forge-health.py
        ├── install.py
        ├── wizard.py
        ├── preflight.sh
        ├── verify-state.sh
        └── write-checkpoint.py
```

## Helper scripts

After establishing an exact worktree:

```bash
bash .agents/skills/sloar-chat-coder/scripts/preflight.sh
bash .agents/skills/sloar-chat-coder/scripts/verify-state.sh "$EXPECTED_COMMIT" "$EXPECTED_TREE" .
python3 .agents/skills/sloar-chat-coder/scripts/write-checkpoint.py \
  --worktree . \
  --repository owner/repository \
  --stage VERIFY
```

## What Sloar intentionally does not do

Sloar does not choose your framework, package manager, database, browser, test stack, coding style, deployment platform, or branch policy. The target repository remains authoritative for engineering method. Sloar only controls continuity, exactness, escalation, publication safety, onboarding capability discovery, forge resilience, and evidence.

## Status

Current version: **0.4.0**

0.4.0 adds Forge Resilience: separate local/remote health, `REMOTE_PARTIAL` vs `REMOTE_DEGRADED`, bounded health probes, deterministic observed-failure classification, retry-storm prevention, outage/capability checkpoints, and mandatory remote-base revalidation before delayed publication.

## License

MIT. See [LICENSE](LICENSE).
