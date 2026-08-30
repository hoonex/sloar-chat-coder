# Sloar Chat Coder

Reliable repository engineering across disposable AI coding sessions.

Sloar Chat Coder is an Agent Skill for coding from chat surfaces where the execution sandbox can disappear, repository state can move concurrently, connected tools may fail, and the host itself may stall before a final response is delivered.

Its goal is simple: **make repository work recoverable, exact, and evidence-bounded — even for a first-time user who has never configured an AI coding workspace before.**

> Durable truth over conversation memory. Evidence before completion claims.

## Start here

You do **not** need to understand Sloar's state machine before using it.

### Preferred: chat-native first use

When the current chat has authorized repository write/execution capability, start with the repository and the task:

```text
Use Sloar for https://github.com/OWNER/REPO and continue with my request.
```

The agent should inspect the current capabilities, preserve repository guidance, install or restore the stable Sloar core when a safe durable path exists, re-resolve repository identity, and begin the requested work. It must not claim durable installation when the current session cannot actually write it.

After normal work, a rollover can be requested naturally:

```text
prepare a handoff
```

A durable handoff returns one fresh-chat control sentence:

```text
Resume the latest Sloar session for OWNER/REPO.
```

The fresh chat reloads compact durable task state, revalidates the repository before trusting the checkpoint, and continues without requiring the previous conversation to be reconstructed.

See [`.agents/skills/sloar-chat-coder/references/chat-native-continuity.md`](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md) for the exact rollover contract and host capability boundaries.

### Upgrade an active older Sloar session

You do not need to open a new chat or restate the current task. In the running session, ask the agent to upgrade Sloar and preserve the work in progress:

```text
Upgrade this active Sloar session to the latest stable release, preserve the current task state, and continue the work.
```

A valid in-session upgrade must re-resolve repository identity first, replace only Sloar-owned files, verify the new release, bridge the current task into the current continuity model, and continue the same task. It must not reset the product branch or ask the user to reconstruct prior progress.

Local/manual fallback from a checkout of the newer Sloar release:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/your-project \
  --upgrade
```

`--upgrade` backs up the previous installed Sloar under `.git/sloar-upgrade-backups/`, upgrades only `sloar-chat-coder`, preserves unrelated companion skills and product files, refuses downgrades, and will not silently overwrite a divergent same-version installation.

See [`.agents/skills/sloar-chat-coder/references/upgrading.md`](.agents/skills/sloar-chat-coder/references/upgrading.md) for the exact upgrade contract.

### If the previous response never finishes

Sloar 0.6 does **not** claim to control the ChatGPT/app/server spinner or to cancel/restart a stuck host generation. For long or interruption-prone repository turns, it can instead persist engineering state so a fresh chat can recover without guessing or blindly repeating completed work.

A useful fresh-chat request is:

```text
The previous Sloar task appears stuck while answering. Inspect the durable turn state and current repository, then recover or continue it safely.
```

A terminal prior turn is reported as `TERMINAL_REPLAY_AVAILABLE`. An unterminated turn is `ACTIVE_OR_INTERRUPTED`; elapsed time alone does not prove the old host is dead. Explicit takeover creates a new turn ID and increments a fencing epoch so a stale old session can be rejected on later guarded writes.

See [docs/INTERRUPTED_TURNS.md](docs/INTERRUPTED_TURNS.md) and [`.agents/skills/sloar-chat-coder/references/operational-continuity.md`](.agents/skills/sloar-chat-coder/references/operational-continuity.md).

### Local/manual fallback

If the current chat cannot perform a safe durable bootstrap, use the installer:

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

A downloaded ZIP works too; extract it and run the same installer from the extracted directory.

The installer copies the skill into `.agents/skills/sloar-chat-coder/` and adds an idempotent Sloar entry block to the target repository's `AGENTS.md`. It does not overwrite unrelated repository guidance.

Preview first with `--dry-run` when desired.

Inside the target repository, the First Run Wizard remains available:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

The default output is deliberately short. It checks the local repository/execution side and marks ChatGPT/Codex GitHub, CI, browser, Plugin/App state as `unknown` until the agent verifies its actual current tools. Use `--json` for the full readiness report.

A minimal local first prompt is:

```text
Use Sloar Chat Coder for this repository. Run the first-run capability check before modifying anything, then recover the exact repository state and continue the task.
```

Read [docs/FIRST_RUN.md](docs/FIRST_RUN.md) for the full beginner path or [README.ko.md](README.ko.md) for Korean.

## New in 0.6: Operational continuity

Sloar 0.6 adds a durable turn layer for long repository work where response delivery itself may fail.

```text
BEGIN_TURN -> ACTIVE -> PROGRESS* -> TERMINALIZE -> visible completion report
```

Key rules:

- engineering terminality and final-response delivery are separate facts;
- terminal state should be persisted before the final visible completion report when a durable transport is available;
- `TERMINAL_REPLAY_AVAILABLE` lets a fresh chat revalidate and report completed/partial/blocked work without redoing it;
- `ACTIVE_OR_INTERRUPTED` does not assume an old host is dead merely because hours or days elapsed;
- takeover requires explicit user intent and increments a monotonic fencing epoch;
- later guarded durable writes check `turn_id + epoch`, reducing stale-session duplicate writes after takeover;
- fencing cannot retroactively cancel a write already in flight before the epoch changed;
- local turn state defaults to `.git/sloar-turn-state/`; authorized cross-chat transport can mirror needed state to `.sloar/turns/` on `sloar/rollover-state`.

Local helper:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/turn-state.py begin . \
  --goal "Finish settings" \
  --response-language "ko-KR"
```

Operational continuity also generalizes several long-lived repository practices:

- separate current repository identity from verification and serving-runtime anchors when evidence shows they differ;
- keep a compact hot working set and colder decision/failure history instead of replaying all project history into every chat;
- match evidence type/scope to the claim being made;
- preserve a minimal failed-experiment record when it prevents repeating the same structural mistake;
- use a compact `changed / preserved / deliberately_not_changed / limitations` boundary for substantial work.

These rules do not override a target repository's engineering policy.

## 0.5: Chat-native continuity

Sloar 0.5 adds a durable old-chat → fresh-chat continuity path without making checkpoint metadata authoritative.

```text
BOOTSTRAP_SESSION? -> NORMAL_WORK -> PREPARE_ROLLOVER -> RESUME_SESSION -> NORMAL_WORK
```

Key rules:

- first-time users can begin from a repository URL when the current session can safely bootstrap Sloar;
- active older Sloar sessions can transition through `UPGRADE_SESSION` without restarting the task;
- `sloar/rollover-state` is the preferred sidecar branch for durable rollover metadata;
- the product branch stays free of runtime checkpoint files;
- fresh sessions revalidate repository reality before trusting checkpoint facts;
- remote-only sessions may mark local working-tree state as unobserved instead of pretending it is clean;
- checkpoint `response_language` is separate from English control/protocol text;
- if host policy forces visible output before durable language reads, Sloar records `PRE_RESPONSE_READ_BLOCKED` and does not claim the strict first-response language gate passed;
- unchanged blocked validation is not retried without changed host capability/evidence.

Local checkpoint helper:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/session-rollover.py handoff . \
  --goal "Finish settings" \
  --active "desktop UI" \
  --next "run browser regression" \
  --response-language "ko-KR"
```

Local helper state defaults to `.git/sloar-rollover/`, so generating a checkpoint does not dirty the product worktree.

## 0.4: Forge resilience

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
- long conversations can compress or lose working context;
- a host can stall before a final visible response is delivered even after repository work changed durable state.

Sloar treats those as engineering constraints rather than exceptions.

## The model

Every repository task moves through an explicit lifecycle:

```text
RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

Before that lifecycle begins, a first-time environment may run a lightweight **ONBOARD** capability check. An explicit version change inside a running task may enter the bounded `UPGRADE_SESSION` transition without resetting the task lifecycle. Long/interruption-prone work may additionally use the turn overlay without replacing the repository task lifecycle.

Publication/recovery is guarded by these concepts:

- **Repository identity** — commit SHA + tree SHA + working-tree state.
- **Verification/runtime anchors** — distinguish current source from exact verified/serving states when evidence shows they differ.
- **Capability ladder** — use the lowest sufficient execution/transport level.
- **Forge overlay** — distinguish `REMOTE_HEALTHY`, `REMOTE_PARTIAL`, and `REMOTE_DEGRADED`.
- **Failure fingerprint** — same failure + same inputs means change strategy, not blind retry.
- **Evidence ledger** — no verification evidence means no completion claim; evidence scope must match claim scope.
- **Turn fence** — an ACTIVE durable turn must still own its `turn_id + epoch` before guarded durable writes.

## Core invariants

1. Durable repository state outranks reconstructed conversation memory.
2. Establish exact repository identity before modification.
3. Prefer the sandbox work container over remote execution.
4. Use the lowest sufficient capability level.
5. Diagnose a failure before retrying or changing source.
6. Completion claims are bounded by collected evidence and evidence scope.
7. Revalidate mutable remote state immediately before publication; when turn fencing is active, validate the current epoch too.
8. Missing setup, one missing permission, or a stuck host response must not be confused with a product/repository failure.

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
│   ├── FORGE_RESILIENCE.ko.md
│   ├── INTERRUPTED_TURNS.md
│   └── INTERRUPTED_TURNS.ko.md
├── tests/
│   ├── test_chat_native_contract.py
│   ├── test_session_rollover.py
│   ├── test_turn_state.py
│   └── test_upgrade.py
└── .agents/skills/sloar-chat-coder/
    ├── SKILL.md
    ├── references/
    │   ├── capability-ladder.md
    │   ├── chat-native-continuity.md
    │   ├── concurrency.md
    │   ├── evidence-ledger.md
    │   ├── forge-resilience.md
    │   ├── operational-continuity.md
    │   ├── recovery.md
    │   ├── state-machine.md
    │   ├── upgrading.md
    │   └── verification.md
    └── scripts/
        ├── doctor.py
        ├── forge-health.py
        ├── install.py
        ├── session-rollover.py
        ├── turn-state.py
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

Sloar does not choose your framework, package manager, database, browser, test stack, coding style, deployment platform, or branch policy. The target repository remains authoritative for engineering method. Sloar also does not control the host application's response spinner or server-side generation lifecycle. Sloar controls continuity, exactness, escalation, publication safety, onboarding capability discovery, active-session upgrades, planned chat rollover, interrupted-turn recovery, forge resilience, and evidence boundaries.

## Status

Current version: **0.6.0**

0.6.0 adds operational continuity for interrupted/stuck-response turns, durable terminal snapshots, explicit takeover fencing, repository/verification/runtime anchors, and stronger claim/evidence matching while keeping host-level response control outside Sloar's claimed capabilities.

## License

MIT. See [LICENSE](LICENSE).