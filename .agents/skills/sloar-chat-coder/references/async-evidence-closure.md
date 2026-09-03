# Async evidence closure

Use this contract for consequential asynchronous/stateful work where correctness can change across an await, callback, retry, cancellation, session switch, invalidation, reconnect, subscription event, or queued operation.

The goal is not to enumerate every possible race. The goal is to derive the relevant race surface from the requested behavior and prove the observable contract rather than only internal state.

## Split compound requirements before claiming PASS

Do not let one passing proxy close several independently observable requirements. If different code paths can satisfy or violate parts of one sentence independently, track those parts independently in the claim-to-evidence map.

Example: logout fencing and explicit invalidation fencing require separate evidence when they use different paths.

## Await-boundary state-transition analysis

For each consequential async operation, model:

START -> SUSPEND / external work -> INTERVENING TRANSITION* -> RESUME -> OBSERVABLE RESULT

Derive relevant transitions from the feature. Common classes include identity/session switch, invalidate/delete/replace, newer local mutation, newer remote event/version, online/offline, cancel/dispose, retry/reconnect, new queue work, and ownership/epoch/generation change.

For each transition that can change correctness, ask both:
1. Can the resumed operation mutate internal, cached, or visible state incorrectly?
2. Can it return, resolve, reject, emit, or report an obsolete observable result even if internal state is protected?

A stale result that is prevented from writing state can still violate the public contract if the caller observes that stale value.

## Observable-result invariant

Verification must cover the externally observable surface promised by the API, not only final store contents. Depending on the API this may include return values, Promise resolution values, rejection/error class, callback payload, emitted event, visible state, cache state, remote side effects, queue state, and request count/deduplication.

Do not mark an async race fixed merely because get() or final UI is correct when await operation() can still return stale data.

## Lifecycle-pair derivation

When two lifecycle actions can overlap, derive pairwise race candidates from actual ownership boundaries. Examples include load x invalidate, load x edit, load x push, flush x enqueue, flush x offline, mutation x logout, retry x invalidation, and cancel x shared in-flight work.

Do not blindly test a Cartesian product. Select pairs where both actions touch the same semantic owner, generation, queue, cache key, visible projection, or remote side effect. At least one test should force the transition to occur during the suspended phase when ordering matters. Sequential tests are not evidence for an interleaving race.

## Fencing must be end-to-end

A generation, token, or epoch is useful only if every consequential consumer checks the appropriate fence. Trace the path from request start through cache/in-flight layer, coordinator/service layer, visible/local state, and returned/emitted result.

A lower layer preventing cache repopulation does not prove an upper layer cannot write the stale response elsewhere or return it to the caller.

## Retry, queue, and liveness closure

For retryable or queued work, prove both safety and liveness: no duplicate/obsolete effect, and valid pending work can still make progress later.

Relevant checks may include rejected in-flight cleanup, stable idempotency identity after ambiguous remote apply, releasing drain state after completion/failure, avoiding stranded work near drain completion, stopping later sends after an offline/cancel transition when required, and allowing a later reconnect/retry to resume retained work.

## Claim discipline

Before reporting PASS for an async requirement, bind it to evidence exercising the same operation path and relevant interleaving. Use PARTIAL or EVIDENCE_GAP when the implementation appears structurally correct but the required interleaving or observable surface was not executed.

Do not generalize from logout test to all invalidation paths, final-state test to Promise return value, sequential test to concurrent interleaving, cache fence to coordinator fence, or one successful flush to future drain liveness.

The purpose is to improve reasoning coverage, not inflate test count. Prefer a small adversarial set that directly attacks identified state transitions.
