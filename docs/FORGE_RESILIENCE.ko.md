# Forge 장애 대응

Sloar 0.4는 **로컬 Git 저장소**와 그 주변의 **호스팅 Forge 플랫폼**을 서로 다른 장애 영역으로 취급합니다.

GitHub 장애가 PR, API, Actions, 검색, checks, webhook, artifact에 영향을 주더라도 로컬 commit/tree 자체는 정상일 수 있습니다. Sloar는 원격 서비스 하나가 흔들린다는 이유로 정상적인 로컬 작업을 버리거나 같은 요청을 무한 재시도하지 않습니다.

## 핵심 규칙

정확한 소스가 로컬에 있고 로컬 검증도 가능하다면:

```text
LOCAL_READY + REMOTE_DEGRADED = 로컬 작업은 계속, publication만 보류
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

`--probe`는 Git transport를 한 번 확인합니다. GitHub origin이고 인증된 `gh` CLI가 있다면 GitHub repository API도 한 번 확인합니다. 서비스가 살아날 때까지 반복 실행하는 루프는 만들지 않습니다.

## 장애 중 해야 할 일

1. 로컬 HEAD/tree/working-tree 증거를 보존합니다.
2. 저장소 규칙이 허용하면 구현과 로컬 검증은 계속합니다.
3. disposable workspace가 사라질 수 있다면 checkpoint를 남깁니다.
4. publication과 remote verification은 pending으로 표시합니다.
5. 같은 forge-layer failure fingerprint가 반복되면 동일 요청을 계속 재시도하지 않습니다.
6. 서비스가 복구되면 publication 전에 remote base를 다시 확인합니다.

## Mirror

Mirror는 선택 사항입니다. Primary forge가 장애라는 이유만으로 Sloar가 임의로 GitLab/Forgejo/GitHub mirror를 만들거나 private source를 다른 제공자에 올리면 안 됩니다.

사용자/저장소가 이미 mirror를 허용한 경우에만 정확한 commit identity를 확인해서 사용하고, primary forge가 복구되면 의도적으로 reconcile합니다.

전체 규칙은 `.agents/skills/sloar-chat-coder/references/forge-resilience.md`를 참고하세요.
