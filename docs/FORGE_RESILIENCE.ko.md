# Forge 장애 대응

Sloar 0.4는 **로컬 Git 저장소**와 그 주변의 **호스팅 Forge 플랫폼**을 서로 다른 장애 영역으로 취급합니다.

GitHub 장애가 PR, API, Actions, 검색, checks, webhook, artifact에 영향을 주더라도 로컬 commit/tree 자체는 정상일 수 있습니다. 반대로 GitHub 서비스는 정상인데 현재 App/token에 특정 작업 권한만 없을 수도 있습니다. Sloar는 이 둘을 같은 장애로 취급하지 않습니다.

## 핵심 규칙

원격 서비스 자체가 불안정하지만 정확한 소스와 로컬 검증이 가능하다면:

```text
LOCAL_READY + REMOTE_DEGRADED = 로컬 작업은 계속, publication만 보류
```

Forge는 살아 있지만 현재 인증/정책으로 필요한 작업을 수행할 수 없다면:

```text
LOCAL_READY + REMOTE_PARTIAL = 검증된 tree를 보존하고, 같은 권한으로 재시도하지 말고 capability/policy 경로를 바꿈
```

PR 생성, CI 성공, 배포 성공 같은 원격 결과는 실제 증거가 생기기 전에는 성공했다고 말하지 않습니다.

## 로컬과 원격 상태 분리 확인

네트워크 요청 없이 로컬만 확인:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

자동 재시도 없는 1회 원격 probe:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

다른 agent/tool이 결과를 읽어야 한다면 `--json`을 사용합니다.

`--probe`는 Git transport를 한 번 확인합니다. GitHub origin이고 인증된 `gh` CLI가 있다면 GitHub repository API도 한 번 확인합니다. 단, repository API가 정상이라고 해서 workflow write, merge, release 같은 모든 권한이 있다는 뜻은 아닙니다.

## 이미 발생한 오류 분류

네트워크 요청 없이 기존 로그만 분류할 수 있습니다.

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

또는 짧은 오류라면:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-error 'rejected non-fast-forward; fetch first'
```

대표 분류:

- GitHub App이 workflow 파일을 수정하지 못함 → `CAPABILITY_MISMATCH / REMOTE_PARTIAL`
- CI가 `action_required`/승인을 요구함 → `REMOTE_ACTION_REQUIRED / REMOTE_PARTIAL`
- branch protection/ruleset 거절 → `POLICY_BLOCKED / REMOTE_PARTIAL`
- non-fast-forward/stale lease → `REMOTE_MOVED`, remote base를 다시 확인하고 reconcile
- 429/rate limit → `REMOTE_DEGRADED`, 즉시 반복 재시도 금지
- 5xx/DNS/timeout → `REMOTE_DEGRADED`

출력에는 normalized class, layer, retry 전략, 다음 행동, SHA-256 fingerprint가 포함되며 **원본 오류 문자열은 다시 출력하지 않습니다.**

## 서비스 장애 중 해야 할 일

1. 로컬 HEAD/tree/working-tree 증거를 보존합니다.
2. 저장소 규칙이 허용하면 구현과 로컬 검증은 계속합니다.
3. disposable workspace가 사라질 수 있다면 checkpoint를 남깁니다.
4. publication과 remote verification은 pending으로 표시합니다.
5. 같은 forge-layer failure fingerprint가 반복되면 동일 요청을 계속 재시도하지 않습니다.
6. 서비스가 복구되면 publication 전에 remote base를 다시 확인합니다.

## 권한/정책 문제일 때

1. 이미 검증된 product tree를 보존합니다.
2. 같은 identity + 같은 permission으로 같은 write를 반복하지 않습니다.
3. 다른 transport는 이미 허가되어 있거나 사용자/저장소가 명시적으로 허용했을 때만 사용합니다.
4. 가능하면 막힌 작업만 분리합니다. 예: product 파일 publication과 workflow 파일 수정 분리.
5. 나중에 권한이 생기더라도 write 직전에 remote base/head를 다시 확인합니다.

## Mirror

Mirror는 선택 사항입니다. Primary forge가 장애이거나 권한이 부족하다는 이유만으로 Sloar가 임의로 GitLab/Forgejo/GitHub mirror를 만들거나 private source를 다른 제공자에 올리면 안 됩니다.

사용자/저장소가 이미 mirror를 허용한 경우에만 정확한 commit identity를 확인해서 사용하고, primary forge가 복구되면 의도적으로 reconcile합니다.

전체 규칙은 `.agents/skills/sloar-chat-coder/references/forge-resilience.md`를 참고하세요.
