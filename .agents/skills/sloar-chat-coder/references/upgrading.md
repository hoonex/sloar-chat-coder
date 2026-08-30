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
4. If the installed version already equals the intended stable version, do not rewrite files. Continue the task and, when appropriate, create the first rollover checkpoint for this session.
5. Upgrade only Sloar-owned files. Preserve unrelated target repository guidance, product source, task branches, tests, CI configuration, and companion skills unless their own upgrade is explicitly requested.
6. Before replacing an existing local Sloar directory, preserve it outside the worktree. The bundled installer uses `.git/sloar-upgrade-backups/` so a custom or partially modified old installation can be recovered without dirtying the product tree.
7. Never use a blind recursive replacement when the old installation cannot be identified or safely preserved. If the current environment cannot preserve the old Sloar files, stop the upgrade write and continue the existing task under the old version rather than risking unrelated repository state.
8. After installing the new Sloar files, verify the installed version and run the strongest available Sloar self-test/helper validation appropriate to the current environment.
9. Re-resolve repository identity after the upgrade. Treat any unexpected non-Sloar product change as a reconciliation event.
10. Bridge the active old session into the new continuity model: compact the current goal, completed/active/pending work, durable decisions, evidence, blockers, next action, response language, and current observable repository identity into the first checkpoint supported by the new release.
11. Persist that checkpoint through the strongest authorized durable path. For 0.5+, prefer `sloar/rollover-state` when repository write is available.
12. Continue the user's current task immediately. An upgrade is maintenance of the running session, not a new project or a reason to restart the conversation.

## Entry conditions

Enter `UPGRADE_SESSION` only when:

- an older installed Sloar release is durably observable; and
- the user asks to upgrade, or the user explicitly authorizes repository maintenance that includes the upgrade.

Do not silently upgrade merely because a newer release exists.

## Exit conditions

The upgrade is complete only when:

- the installed Sloar version is the intended release;
- the upgrade changed only intended Sloar-owned paths;
- available self-tests/validation passed or any blocker is reported explicitly;
- current repository identity was re-resolved after the write; and
- the active task context is still available, with a new-format rollover checkpoint created when durable checkpoint capability exists.

If verification fails, keep the preserved old installation available and do not claim the upgrade succeeded.

## Local manual fallback

From a checkout of the newer Sloar release:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

`--upgrade` updates only the `sloar-chat-coder` skill, preserves the previous installed skill under Git metadata, and leaves unrelated bundled companion skills untouched.

The old generic `--force` mode remains an explicit replacement mechanism; it is not the recommended version-upgrade path.
