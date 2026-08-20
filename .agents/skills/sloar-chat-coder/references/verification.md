# Change-aware verification

The target repository defines actual commands. Sloar defines how to select and interpret evidence.

## Risk matrix

### Logic/runtime code
Typically require syntax/type/build checks plus focused behavioral tests.

### UI/CSS/interaction
Typically require relevant desktop/mobile viewport checks, console/page-error inspection, overflow/layout checks, and screenshots for interaction states that are visually meaningful.

### Persistence/state migration
Test write, reload/restart, compatibility/migration, and invalid/stale stored state where applicable.

### Network/data flow
Inspect request count, duplicate requests, cancellation/error paths, loading/fallback behavior, and real integration contracts when required.

### Performance-sensitive code
Inspect newly introduced polling, observers, mutation churn, animation loops, timers, repeated layout reads/writes, or request amplification. Measure repository-specific budgets when they exist.

### Deployment/configuration
Require relevant CI plus deployment/route/health evidence. A successful build is not necessarily successful production behavior.

## Failure classification

Before editing source after a failed verification, classify the failure as one of:

- product regression;
- stale/incorrect test;
- environment/capability failure;
- external dependency/integration failure;
- transport/publication corruption;
- permission/auth failure;
- concurrency/stale-base failure;
- unknown.

For `unknown`, inspect more evidence before source changes.

## Retry rule

A single bounded retry can be justified for a clearly transient failure only after logs show a transient mechanism and the retry does not risk duplicate destructive effects. Otherwise change strategy or report the blocker.
