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

## ChatGPT: Plugin, App, and Skill are different things

Modern ChatGPT exposes workflow capabilities through **Plugins**. A plugin can package one or more **Skills** and can depend on **Apps**. Apps are the integrations that authenticate to external systems and provide data/actions such as repository access.

For Sloar this means:

- **Sloar Skill**: the repository-engineering instructions in this project.
- **GitHub App**: the authenticated connection that may give ChatGPT repository read/write capabilities.
- **Plugin**: a discoverable workflow package that can bundle skills and apps. Sloar core does not require a future Sloar Plugin listing to function.

If your ChatGPT surface supports Plugins, GitHub access is configured through the current Plugin/App connection flow when that capability is available, with the underlying app granted access only to the repositories you choose. Exact availability varies by plan, workspace policy, role, surface, and region, so Sloar must inspect actual capabilities instead of assuming them.

See [docs/FIRST_RUN.md](docs/FIRST_RUN.md#chatgpt-setup) for the beginner setup path and [docs/CHATGPT_PLUGINS.md](docs/CHATGPT_PLUGINS.md) for the Plugin/App/Skill decision tree. Sloar is currently distributed as an Agent Skill repository, not as a claimed Plugin Directory listing.

## Why Sloar exists

Chat-based coding has a different failure model from a normal workstation:

- a sandbox can be recreated or lost;
- a branch may move while the agent is working;
- a connected GitHub write path can serialize content incorrectly or partially fail;
- network access may exist in CI but not in the sandbox, or the reverse;
- a failed test can be a product regression, an external dependency failure, or a transport problem;
- long conversations can compress or lose working context.

Sloar treats those as engineering constraints rather than exceptions.

## The model

Every repository task moves through an explicit lifecycle:

```text
RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

Publication is guarded by four concepts:

- **Repository identity** — commit SHA + tree SHA + working-tree state.
- **Capability ladder** — use the lowest sufficient execution/transport level.
- **Failure fingerprint** — same failure + same inputs means change strategy, not blind retry.
- **Evidence ledger** — no verification evidence means no completion claim.

Before that lifecycle begins, a first-time environment may run a lightweight **ONBOARD** capability check. ONBOARD never invents missing permissions and never blocks local work merely because a hosted integration is absent.

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
│   └── CHATGPT_PLUGINS.ko.md
├── examples/
│   ├── checkpoint.example.json
│   ├── readiness.example.json
│   └── first-prompt.md
└── .agents/
    └── skills/
        └── sloar-chat-coder/
            ├── SKILL.md
            ├── references/
            │   ├── actions-missions.md
            │   ├── capability-ladder.md
            │   ├── concurrency.md
            │   ├── environment-onboarding.md
            │   ├── evidence-ledger.md
            │   ├── recovery.md
            │   ├── state-machine.md
            │   └── verification.md
            └── scripts/
                ├── doctor.py
                ├── install.py
                ├── wizard.py
                ├── preflight.sh
                ├── verify-state.sh
                └── write-checkpoint.py
```

## Core invariants

1. Durable repository state outranks reconstructed conversation memory.
2. Establish exact repository identity before modification.
3. Prefer the sandbox work container over remote execution.
4. Use the lowest sufficient capability level.
5. Diagnose a failure before retrying or changing source.
6. Completion claims are bounded by collected evidence.
7. Revalidate mutable remote state immediately before publication.
8. First-run guidance distinguishes missing setup from missing capability; it never pretends a plugin/app is connected.

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

`--worktree` is a local filesystem path. `--repository` is the durable repository identifier recorded in the checkpoint.

## What Sloar intentionally does not do

Sloar does not choose your framework, package manager, database, browser, test stack, coding style, deployment platform, or branch policy. The target repository remains authoritative for engineering method. Sloar only controls continuity, exactness, escalation, publication safety, onboarding capability discovery, and evidence.

## Status

Current version: **0.3.0**

0.3.0 adds a beginner-facing First Run Wizard, a compact readiness contract, safer separation of local vs hosted capability evidence, and a dedicated current-model ChatGPT Plugin/App/Skill guide.

## License

MIT. See [LICENSE](LICENSE).
