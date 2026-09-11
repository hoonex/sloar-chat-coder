# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. 저장소가 움직이거나 도구가 실패해도 추측 대신 durable state와 증거로 이어가게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 repository 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

현재 stable: **0.10.1**

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/stable-0.10.1-2563eb?style=flat-square" alt="stable 0.10.1"></a>
  <a href="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml"><img src="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml/badge.svg?branch=main" alt="Validate Sloar"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-16a34a?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#처음이라면-이-문장부터-복붙"><b>빠른 시작</b></a> ·
  <a href="docs/USER_GUIDE.ko.md"><b>사용자 가이드</b></a> ·
  <a href="#업데이트"><b>업데이트</b></a> ·
  <a href="#새-채팅으로-넘어가기"><b>새 채팅</b></a> ·
  <a href="#웹개발에서는-구조와-디자인을-같이-판단"><b>웹 구조 + 디자인</b></a> ·
  <a href="README.md">English</a>
</p>

> **저장소의 실제 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## ChatGPT 채팅 + GitHub 플러그인으로 사용하는 경우

Sloar는 **현재 채팅의 AI가 읽고 적용하는 작업 지침**이다. GitHub 플러그인은 파일·커밋·PR을 읽고 수정하는 통로이고, 두 기능은 별개다.

| 기능 | 어디서 동작하나 |
| --- | --- |
| 작업 판단·지침 적용 | Sloar 문서를 읽은 현재 ChatGPT 채팅 |
| 코드 읽기·수정·PR·작업 상태 저장 | 현재 세션에 노출된 GitHub 도구 |
| 테스트·빌드 | 실행 환경이 있다면 그 환경, 아니면 사용 가능한 저장소 CI |
| Python 복구/구조 분석 도우미 | 실행 환경이 있을 때만 선택적으로 실행 |
| Codex CLI A/B 평가 | Sloar 개발용 별도 환경; 일반 채팅에서 자동 실행되지 않음 |

**일반 채팅에서 쓰려고 Codex CLI나 API 키를 따로 준비할 필요는 없다.** 실행 도구가 없다면 실행하지 않은 검증은 미확인으로 보고한다. 코드가 저장됐다는 사실과 테스트 통과는 구분한다.

0.10은 채팅에서 직접 체크포인트 JSON을 저장하는 절차와 GitHub 동시 수정 보호를 유지하면서, 웹 저장소를 빠르게 파악하기 위한 증거 기반 architecture capsule을 추가한다. 로컬 잠금이 GitHub까지 잠그는 것은 아니며, 다른 세션과 겹치는 작업은 별도 브랜치에서 진행한다. 원본 Sloar 변경이 다른 저장소에 복사된 버전까지 자동 갱신하지는 않는다.

자세한 절차: [채팅·GitHub 작업 지침](.agents/skills/sloar-chat-coder/references/chat-github-workflow.md).

## 처음이라면: 이 문장부터 복붙

새 ChatGPT/Codex 채팅을 열고 `OWNER/REPO`와 작업 내용만 바꿔서 보낸다.

```text
다음 canonical Sloar Chat Coder를 사용해서 작업해.
https://github.com/hoonex/sloar-chat-coder

대상 저장소를 수정하기 전에 이 세션에서 Sloar를 실제로 로드해:
- 현재 canonical Sloar source를 exact commit SHA로 확인하고;
- 그 exact SHA의 .agents/skills/sloar-chat-coder/SKILL.md를 실제로 읽고;
- 필요한 Sloar reference만 같은 SHA에서 읽어.
canonical Sloar를 실제로 읽을 수 없으면 SLOAR_UNAVAILABLE이라고 보고하고, Sloar 없이 일반/Bare 방식으로 몰래 계속하지 마.

대상 저장소:
https://github.com/OWNER/REPO

원하는 작업:
<여기에 만들거나 수정하고 싶은 내용을 적기>

현재 저장소 상태를 확인한 뒤 진행해.
```

Sloar를 처음 보는 새 채팅에는 **원본 링크와 실제 activation 요구를 같이 넣는 것을 권장한다.** `Use Sloar Chat Coder`라는 이름만 적는 것은 activation 증거가 아니다. 이미 target repository에 Sloar가 설치되어 있다면 세션이 설치된 contract를 직접 읽을 수 있으므로 더 짧게 말해도 된다.

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
| 낯선 웹 저장소/AI 수정이 누적된 웹앱 | 기능만 설명하면 Sloar가 먼저 bounded topology를 잡고 관련 owner만 따라감 |
| 모호한 웹 UI | 디자인 용어를 몰라도 됨. 필요한 질문만 함 |
| 디자인을 맡기기 | `알아서 제일 어울리게 해` |
| 업데이트 | 첫 Sloar 작업/새 채팅 복구 때 stable 1회 확인 후 승인받아 업그레이드 |
| 새 채팅 이동 | `새 채팅으로 넘겨줘.` |
| 답변이 멈춤 | 새 채팅에서 saved turn state와 현재 repository 확인 요청 |

## Sloar 0.10 핵심 구조

0.10은 0.9에서 도입한 compact reasoning kernel을 유지하면서, substantial web 작업 전에 저장소 구조를 증거 기반으로 빠르게 파악하는 architecture discovery를 추가한다.

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

기존 `ONBOARD → RECOVER → IDENTIFY → ...` state machine은 없어지지 않았다. 다만 모든 작업을 기계적으로 통과하는 절차가 아니라 **continuity/publication/recovery 위험이 있을 때 펼쳐 쓰는 guardrail**이다.

사용자 요구의 semantic phase와 내부 상태도 동일시하지 않는다. 예를 들어 `queued`에서 취소가 됐다는 것만으로 `runner가 시작하기 전에 cancel` 조건을 증명하지 않는다. 필요한 경우 callback/microtask가 이미 scheduled됐지만 user runner가 아직 invoke되지 않은 latest valid observable boundary까지 검증한다.

또 final state만 보지 않고 Promise resolve/reject, callback 호출 여부, AbortSignal, dedupe ownership, running/resource count, late finalizer, retry liveness 같은 observable도 확인한다.

자세히:
- [Reasoning kernel](.agents/skills/sloar-chat-coder/references/reasoning-kernel.md)
- [Async evidence closure](.agents/skills/sloar-chat-coder/references/async-evidence-closure.md)
- [Verification](.agents/skills/sloar-chat-coder/references/verification.md)
- [State machine](.agents/skills/sloar-chat-coder/references/state-machine.md)

## 웹개발에서는 구조와 디자인을 같이 판단

### AI가 저장소를 빠르고 정확하게 이해하는 architecture capsule

0.10부터 낯선 웹 저장소나 AI 수정이 반복된 저장소에서는 처음부터 모든 파일을 넓게 읽는 대신 다음 순서로 구조를 잡을 수 있다.

```text
DURABLE SOURCE
→ deterministic topology snapshot
→ evidence-backed semantic owner map
→ task-specific read set
```

실행 환경이 있으면 먼저:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/web-architecture-map.py . --json
```

을 실행한다. 이 도우미는 Git identity, 선언된 framework/router/state/data/styling system, package script, source root, entrypoint candidate, convention-based route, config, token/global-style candidate처럼 **코드에서 비교적 확실하게 읽을 수 있는 사실**만 구조화한다.

그리고 AI가 실제 작업에 필요한 최소 source path를 읽으면서 다음 증거 수준을 구분한다.

```text
DECLARED  package/config가 명시
OBSERVED  repository path/content에서 직접 관찰
CONFIRMED semantic ownership이 source로 직접 확인됨
INFERRED  근거는 있지만 직접 확정되지는 않음
UNKNOWN   아직 해결하지 않음
```

즉 폴더 이름이 `store`라고 해서 곧바로 전역 상태의 authoritative owner라고 단정하지 않는다. 구조 지도는 source truth를 대체하는 문서가 아니라 **어디부터 읽어야 할지 알려주는 탐색 캐시**다.

작업별로 주로 다음 경로를 따라간다.

```text
route/page
→ data/cache
→ domain/application state
→ component/rendering
→ styling/tokens
→ async/interaction lifecycle
→ persistence/navigation/external side effects
```

자세히:
- [Web architecture capsule](.agents/skills/sloar-chat-coder/references/web-architecture-capsule.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)

### 디자인 판단과 product craft

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

0.10부터는 내부 구조도 UI 품질의 일부로 본다. `VISUAL / BEHAVIOR / STRUCTURE / RESILIENCE / HYGIENE`를 별개 claim으로 취급해, 화면이 예쁘거나 build가 GREEN인 것만으로 duplicate state, effect lifecycle, CSS/token ownership, obsolete path가 정상이라고 간주하지 않는다.

Apple 스타일이 명시적으로 요청된 작업에서는 복잡성을 괜히 노출하지 않기, 익숙하게 배울 수 있는 novelty, endpoint뿐 아니라 상태 전환 자체 설계, 유지보수 비용을 정당화하는 신기술, 작은 delight budget을 적용한다. 단 polish가 접근성·성능·구조를 대신할 수는 없다.

자세히:
- [web-design-guidance](.agents/skills/web-design-guidance/SKILL.md)
- [Adaptive discovery](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)
- [Apple 전문 companion](.agents/skills/apple-web-design/SKILL.md)

## 업데이트

**업데이트 확인은 자동이고, 설치는 사용자 승인 후 자동이다.**

Sloar가 설치된 저장소에서 현재 채팅의 첫 Sloar repository 작업을 시작하거나 새 채팅에서 resume/takeover할 때 canonical stable을 확인할 수 있으면 1회만 installed 버전과 비교한다.

```text
설치 버전 == stable
→ 아무 알림 없이 작업 계속

새 stable 있음
→ Sloar update available: 0.9.1 -> 0.10.0. Upgrade now?
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
  --stable-version 0.10.0 --json
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
- [Web architecture capsule](.agents/skills/sloar-chat-coder/references/web-architecture-capsule.md)
- [Evidence ledger](.agents/skills/sloar-chat-coder/references/evidence-ledger.md)
- [일반 웹 디자인 companion](.agents/skills/web-design-guidance/SKILL.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)
- [Sloar core Skill](.agents/skills/sloar-chat-coder/SKILL.md)

## License

MIT. [LICENSE](LICENSE)