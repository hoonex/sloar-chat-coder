# Upgrading an active Sloar session

Use this procedure when a repository is already using an older Sloar release and the user wants to upgrade without losing the current development state.

## User-facing intent

Accept ordinary requests such as:

```text
이 세션 Sloar 최신 버전으로 업그레이드하고 현재 작업 상태는 유지한 채 계속해.
```

The user should not need to start a fresh chat, restate the task, or manually reconstruct prior progress.

## UPGRADE_SESSION

1. Re-resolve the target repository and the exact currently observable repository identity before changing Sloar files.
2. Read the installed `.agents/skills/sloar-chat-coder/SKILL.md` and record the installed Sloar version. Do not infer the version from conversation memory.
3. Resolve the intended stable Sloar release independently. `latest main` is acceptable only when the repository itself documents that exact version as the current stable release.
4. If the installed version already equals the intended stable version, do not rewrite the Sloar core merely to refresh it. Continue the task and, when appropriate, create the current rollover/turn checkpoint for this session.
5. Upgrade only Sloar-owned paths. Preserve unrelated target repository guidance, product source, task branches, tests, CI configuration, and unrelated skills.
6. A newer Sloar release may add or update a **bundled companion skill**. Missing companions may be installed. An older companion may be auto-upgraded only when its complete installed file fingerprint exactly matches a Sloar-recorded official historical bundle. This proves the installed copy is an untouched known release rather than merely assuming that a lower version is safe to overwrite.
7. If an existing companion differs from the known official fingerprint, has no recognized historical fingerprint, or otherwise appears customized, preserve it. A version number alone is never enough authorization to replace companion content. Report the preserved customization so the user can choose a manual migration later.
8. Before replacing an exact known older companion, back it up under `.git/sloar-upgrade-backups/companions/<name>/`. The backup remains outside the product worktree.
9. Sloar may refresh only its own marker block inside `AGENTS.md` so the installed release can advertise new bundled companions or activation rules. Text outside the `<!-- sloar-chat-coder:begin --> ... <!-- sloar-chat-coder:end -->` block must remain untouched.
10. Before replacing an existing local Sloar core directory, preserve it outside the worktree. The bundled installer uses `.git/sloar-upgrade-backups/` so a custom or partially modified old installation can be recovered without dirtying the product tree.
11. Never use a blind recursive replacement when the old installation cannot be identified or safely preserved. If the current environment cannot preserve the old Sloar files, stop the upgrade write and continue the existing task under the old version rather than risking unrelated repository state.
12. After installing the new Sloar files, verify the installed core version, bundled companion state, and strongest available Sloar self-test/helper validation appropriate to the current environment.
13. Re-resolve repository identity after the upgrade. Treat any unexpected non-Sloar product change as a reconciliation event.
14. Bridge the active old session into the new continuity model: compact the current goal, completed/active/pending work, durable decisions, evidence, blockers, next action, response language, and current observable repository identity into the first checkpoint supported by the new release.
15. Persist that checkpoint through the strongest authorized durable path. For 0.5+, prefer `sloar/rollover-state` when repository write is available.
16. Continue the user's current task immediately. An upgrade is maintenance of the running session, not a new project or a reason to restart the conversation.

## Entry conditions

Enter `UPGRADE_SESSION` only when:

- an older installed Sloar release is durably observable; and
- the user asks to upgrade, or the user explicitly authorizes repository maintenance that includes the upgrade.

Do not silently upgrade merely because a newer release exists.

## Exit conditions

The upgrade is complete only when:

- the installed Sloar core version is the intended release;
- the upgrade changed only intended Sloar-owned paths, safely migrated known-official companions, newly missing bundled companions, and the Sloar-owned `AGENTS.md` marker when applicable;
- pre-existing customized or unrecognized companion skills were preserved unless the user explicitly authorized replacement;
- any automatically replaced historical companion had an exact known fingerprint and a Git-metadata backup;
- available self-tests/validation passed or any blocker is reported explicitly;
- current repository identity was re-resolved after the write; and
- the active task context is still available, with a current rollover/turn checkpoint created when durable checkpoint capability exists.

If verification fails, keep preserved old installations available and do not claim the upgrade succeeded.

## 0.7 -> 0.8 design companion migration

Sloar 0.8 knows the exact official `web-design-guidance` 0.7.0 file fingerprint.

Therefore:

```text
official untouched web-design-guidance 0.7.0
-> backup under .git
-> auto-upgrade to 0.8.0

modified/customized 0.7.0
-> preserve as-is
-> do not infer permission from the old version number
```

This lets ordinary users receive Adaptive Design Discovery / Design Taxonomy / Anti-AI-Slop guidance without sacrificing local design-companion customizations.

## Local manual fallback

From a checkout of the newer Sloar release:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

`--upgrade` safely upgrades the `sloar-chat-coder` core, preserves the previous core under Git metadata, installs missing companions, upgrades only exact known-official older companion bundles, preserves divergent/customized companions, and refreshes only Sloar's owned marker block in `AGENTS.md` when needed.

The generic `--force` mode remains an explicit replacement mechanism; it is not the recommended version-upgrade path.
