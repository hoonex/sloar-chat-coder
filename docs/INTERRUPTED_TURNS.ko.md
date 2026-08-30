# 답변이 끝나지 않을 때 — Sloar interrupted-turn recovery

ChatGPT 같은 호스트에서 개발 작업이 오래 걸릴 때 드물게 **답변이 계속 진행 중으로 표시되지만 최종 응답이 끝나지 않는 상태**가 생길 수 있다.

Sloar는 ChatGPT 앱/서버의 스피너 자체를 강제로 종료하거나 멈춘 실행 프로세스를 되살릴 수는 없다. 대신 0.6부터는 장시간 저장소 작업을 **durable turn**으로 기록해서, 최종 답변이 전달되지 않아도 새 채팅에서 정확한 작업 상태를 복구할 수 있게 한다.

## 핵심 아이디어

```text
작업 시작
  -> ACTIVE turn 기록
  -> 중요한 진행 지점만 progress snapshot
  -> 작업이 끝나면 최종 채팅 답변보다 먼저 terminal snapshot
  -> 사용자에게 최종 답변
```

따라서 코드/PR/CI 작업은 이미 끝났는데 마지막 답변 UI만 멈춘 경우, 새 채팅은 terminal snapshot과 현재 GitHub 상태를 대조한 뒤 **작업을 다시 하지 않고 결과를 복구**할 수 있다.

## 이전 채팅이 멈춘 것 같을 때

새 채팅에서 다음처럼 요청한다.

```text
이전 Sloar 작업이 답변 중에 멈춘 것 같아. 저장된 turn 상태와 현재 저장소를 확인해서 이어서 진행해.
```

Sloar가 마지막 turn을 확인했을 때:

- `TERMINAL_REPLAY_AVAILABLE`이면 작업은 terminal state까지 기록된 것이다. 현재 저장소를 다시 검증한 뒤 결과를 복구한다.
- `ACTIVE_OR_INTERRUPTED`이면 이전 실행이 정말 죽었다고 시간만 보고 단정하지 않는다. 저장소 변경 여부부터 확인한다.

## takeover

`ACTIVE_OR_INTERRUPTED` 상태에서 사용자가 새 채팅에서 계속하라고 명시적으로 요청하면 takeover할 수 있다.

Takeover는 새 `turn_id`와 더 높은 `epoch`를 만든다.

```text
old turn: epoch 4
new turn: epoch 5
```

이후 durable write/publication 전에 현재 turn이 최신 epoch를 소유하는지 확인한다. 예전 채팅이 나중에 갑자기 살아나더라도 다음 write에서 stale fence를 감지하고 중단하게 하는 것이 목적이다.

**시간이 오래 지났다는 이유만으로 자동 takeover하지 않는다.** 1일이나 2일 동안 답변 중으로 보이는 것 자체는 이전 host process가 절대로 돌아오지 않는다는 증거가 아니다.

## Sloar가 해결할 수 없는 부분

다음은 호스트 자체의 영역이다.

- 앱 화면에서 계속 도는 응답 스피너를 강제로 종료하기
- 멈춘 ChatGPT 서버-side generation을 직접 cancel/restart하기
- 이미 in-flight 상태로 시작된 외부 write를 소급 취소하기

Sloar가 제공하는 것은 **손실 없는 복구, 중복 작업 억제, stale session fencing, 정확한 완료 상태 재구성**이다.

## Blank app에서 가져온 운영 개념

장기간 실제 개발 프로젝트에서 효과가 있었던 패턴을 Sloar용으로 일반화했다.

- 현재 repository HEAD와 마지막 검증 상태/실제 runtime 상태를 별도 anchor로 관리
- 다음 행동에 필요한 짧은 hot state와 오래된 결정/실패 기록인 cold history 분리
- CI GREEN이라는 이유만으로 모든 종류의 성공을 주장하지 않고 claim에 맞는 evidence 요구
- 실패한 실험은 성공 작업에 숨기지 않고 다음 반복을 막을 만큼만 기록
- substantial change는 `changed / preserved / deliberately_not_changed / limitations` 경계를 남김

이 규칙들은 특정 제품의 UI/API 정책을 Sloar가 대신 정하는 것이 아니다. 대상 저장소의 engineering rules가 항상 우선한다.
