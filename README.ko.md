# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. 저장소가 움직이거나 도구가 실패해도 추측 대신 durable state와 증거로 이어가게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 repository 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

현재 stable: **0.9.0**

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/stable-0.9.0-2563eb?style=flat-square" alt="stable 0.9.0"></a>
  <a href="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml"><img src="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml/badge.svg?branch=main" alt="Validate Sloar"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-16a34a?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#처음이라면-이-문장부터-복붙"><b>빠른 시작</b></a> ·
  <a href="docs/USER_GUIDE.ko.md"><b>사용자 가이드</b></a> ·
  <a href="#업데이트"><b>업데이트</b></a> ·
  <a href="#새-채팅으로-넘어가기"><b>새 채팅</b></a> ·
  <a href="#웹개발에서는-디자인도-같이-판단"><b>디자인</b></a> ·
  <a href="README.md">English</a>
</p>

> **저장소의 실제 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 처음이라면: 이 문장부터 복붙

새 ChatGPT/Codex 채팅을 열고 `OWNER/REPO`와 작업 내용만 바꿔서 보낸다.

```text
다음 Sloar Chat Coder를 사용해서 이 저장소를 개발해.
Sloar: https://github.com/hoonex/sloar-chat-coder

대상 저장소:
https://github.com/OWNER/REPO

원하는 작업:
<여기에 만들거나 수정하고 싶은 내용을 적기>

먼저 Sloar 사용법과 현재 저장소 상태를 확인한 뒤 진행해.
```

Sloar를 처음 보는 새 채팅에는 원본 링크까지 같이 주는 것을 권장한다. 이미 설치된 저장소라면 더 짧게 말해도 된다.

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<원하는 작업>
```

전체 사용자 가이드: **[docs/USER_GUIDE.ko.md](docs/USER_GUIDE.ko.md)**

English: [README.md](README.md)

## 자주 하는 것

| 상황 | 사용자에게 필요한 말 |
| --- | --- |
| 처음 사용 | `Sloar:` 링크 + 대상 저장소 + 작업 내용 |
| 평소 개발 | 그냥 원하는 코드 작업 요청 |
| CI는 GREEN인데 실제 버그가 남음 | 실제 증상을 알려주면 owner와 evidence phase를 다시 확인 |
| 모호한 웹 UI | 디자인 용어를 몰라도 됨. 필요한 질문만 함 |
| 디자인을 맡기기 | `알아서 제일 어울리게 해` |
| 업데이트 | 첫 Sloar 작업/새 채팅 복구 때 stable 1회 확인 후 승인받아 업그레이드 |
| 새 채팅 이동 | `새 채팅으로 넘겨줘.` |
| 답변이 멈춤 | 새 채팅에서 saved turn state와 현재 repository 확인 요청 |

## Sloar 0.9 핵심 구조

0.9부터는 긴 state machine을 기본 사고법으로 쓰지 않는다. 기본 reasoning kernel은 다섯 단계다.

```text
OBSERVE
→ MODEL
→ ACT
→ PROVE
→ RECONCILE
```

- **OBSERVE**: 실제 repository/runtime/evidence에서 판단에 필요한 사실만 확인.
- **MODEL**: authoritative owner, invariants, 독립적인 acceptance claim, lifecycle transition을 잡음.
- **ACT**: 가장 작은 coherent structural fix를 적용.
- **PROVE**: 구현이 아니라 claim을 공격. 가장 강한 observable과 boundary에서 검증.
- **RECONCILE**: 실제 publish/report할 durable state와 evidence가 여전히 일치하는지 확인.

기존 `ONBOARD → RECOVER → IDENTIFY → ...` state machine은 없어지지 않았다. 다만 모든 작업을 기계적으로 통과하는 절차가 아니라 **continuity/publication/recovery 위험이 있을 때 펼쳐 쓰는 guardrail**이 됐다.

### 0.9에서 강화된 async 검증

사용자 요구의 semantic phase와 내부 상태를 동일시하지 않는다.

예를 들어:

```text
"runner가 시작하기 전에 cancel하면 실행되면 안 됨"
```

을 검증할 때 단순히 `queued` 상태에서 cancel하는 것만으로 PASS하지 않는다. 필요한 경우:

```text
slot/resource는 이미 예약됨
callback/microtask는 이미 scheduled
하지만 user runner는 아직 invoke되지 않음
→ cancel
→ runner invocation count = 0
→ 예약 resource 회수
```

처럼 **latest valid observable boundary**에서 테스트한다.

또 final state만 보지 않고 Promise resolve/reject, callback 호출 여부, AbortSignal, dedupe ownership, running/resource count, late finalizer, retry liveness 같은 observable도 확인한다.

자세히:
- [Reasoning kernel](.agents/skills/sloar-chat-coder/references/reasoning-kernel.md)
- [Async evidence closure](.agents/skills/sloar-chat-coder/references/async-evidence-closure.md)
- [Verification](.agents/skills/sloar-chat-coder/references/verification.md)
- [State machine](.agents/skills/sloar-chat-coder/references/state-machine.md)

## 웹개발에서는 디자인도 같이 판단

0.8.0부터 bundled `web-design-guidance`는 사용자가 `glassmorphism`, `neumorphism`, `brutalism` 같은 용어를 몰라도 된다는 전제로 동작한다.

요청이 충분히 명확하면 바로 진행하고, 큰 방향을 잘못 고르면 재작업 비용이 큰 경우에만 필요한 질문을 한다.

질문 개수도 고정하지 않는다.

```text
거의 명확함 → 0개
중간 정도 모호함 → 필요한 핵심 질문 1~3개 정도
매우 모호함 → 목적/사용자/플랫폼/느낌 같은 고가치 질문 몇 개
"알아서" → optional 질문 중단
```

이후에는 사용자의 평범한 표현을 여러 디자인 축의 **Design DNA**로 번역한다.

```text
philosophy / tone
material language
composition
interaction language
motion posture
density
typography / color stance
```

그리고 흔한 generated/default UI가 제품 이유 없이 반복되는지도 **Anti-AI-Slop** 관점에서 재검토한다. 특정 색/스타일을 금지하는 것이 아니라 자동 기본값을 제품에 맞는 결정으로 바꾸는 것이 목적이다.

자세히:
- [web-design-guidance](.agents/skills/web-design-guidance/SKILL.md)
- [Adaptive discovery](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- [Apple 전문 companion](.agents/skills/apple-web-design/SKILL.md)

## 업데이트

**업데이트 확인은 자동이고, 설치는 사용자 승인 후 자동이다.**

Sloar가 설치된 저장소에서 현재 채팅의 첫 Sloar repository 작업을 시작하거나 새 채팅에서 resume/takeover할 때 canonical stable을 확인할 수 있으면 1회만 installed 버전과 비교한다.

```text
설치 버전 == stable
→ 아무 알림 없이 작업 계속

새 stable 있음
→ Sloar update available: 0.8.3 -> 0.9.0. Upgrade now?
→ 사용자가 승인
→ 현재 작업 상태를 보존한 안전한 업그레이드 자동 실행

stable 확인 불가
→ update status = unknown
→ 일반 repository 작업은 그대로 계속
```

새 버전이 있다는 이유만으로 사용자 모르게 repository를 덮어쓰지는 않는다. 승인 후에는 백업, Sloar-owned 파일 갱신, known-official companion migration, custom companion 보존, 검증, checkpoint bridge를 수행한다.

직접 시작하려면:

```text
이 세션 Sloar 최신 stable 버전으로 업그레이드하고,
현재 작업 상태는 유지한 채 계속해.
```

로컬 fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

Wizard에 stable을 명시하려면:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py . \
  --stable-version 0.9.0 --json
```

자세한 계약: [upgrading.md](.agents/skills/sloar-chat-coder/references/upgrading.md)

## 새 채팅으로 넘어가기

현재 채팅에서 `새 채팅으로 넘겨줘.`라고 한다.

가능한 환경이면 Sloar는 제품 branch와 분리된 durable checkpoint에 현재 목표, 완료/진행/대기 작업, 결정, 증거, repository identity와 다음 행동을 남긴다.

기본 Resume 문장:

```text
Resume the latest Sloar session for OWNER/REPO.
```

새 채팅은 checkpoint를 그대로 믿지 않고 현재 repository를 다시 확인한 뒤 이어간다.

자세한 계약: [chat-native-continuity.md](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## 답변이 계속 끝나지 않을 때

같은 failure fingerprint에 대해 무한히 `하나만 더`를 반복하지 않는다.

```text
진단
→ 그 진단에 대한 수정 최대 1회
→ 영향받은 검증 재실행
```

같은 실패가 남으면 authoritative ownership boundary를 다시 확인하고, 새로운 evidence가 없으면 `PARTIAL`, `BLOCKED`, `FAILED` 중 맞는 상태로 턴을 끝낸다.

ChatGPT/app/server 자체가 멈춘 경우 새 채팅에서:

```text
이전 Sloar 작업이 답변 중에 멈춘 것 같아.
저장된 turn 상태와 현재 저장소를 확인해서 이어서 진행해.
```

자세한 설명: [docs/INTERRUPTED_TURNS.ko.md](docs/INTERRUPTED_TURNS.ko.md)

## 처음 설치가 자동으로 안 된다면

현재 ChatGPT/Codex 세션에 GitHub write나 code execution capability가 없을 수 있다. 이때 Sloar는 설치됐다고 가장하면 안 된다.

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

First Run Wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

## 문서

**사용자용**
- [사용자 가이드](docs/USER_GUIDE.ko.md)
- [처음 실행](docs/FIRST_RUN.ko.md)
- [연결/권한](docs/CONNECTIONS.ko.md)
- [ChatGPT Plugin/App/Skill](docs/CHATGPT_PLUGINS.ko.md)
- [멈춘 응답/turn 복구](docs/INTERRUPTED_TURNS.ko.md)
- [GitHub/CI 장애 대응](docs/FORGE_RESILIENCE.ko.md)

**엔지니어링/디자인 프로토콜**
- [Reasoning kernel](.agents/skills/sloar-chat-coder/references/reasoning-kernel.md)
- [Async evidence closure](.agents/skills/sloar-chat-coder/references/async-evidence-closure.md)
- [Ownership / evidence closure](.agents/skills/sloar-chat-coder/references/ownership-evidence-closure.md)
- [Evidence ledger](.agents/skills/sloar-chat-coder/references/evidence-ledger.md)
- [일반 웹 디자인 companion](.agents/skills/web-design-guidance/SKILL.md)
- [Sloar core Skill](.agents/skills/sloar-chat-coder/SKILL.md)

## License

MIT. [LICENSE](LICENSE)
