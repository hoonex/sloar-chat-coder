# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. 저장소가 움직이거나 도구가 실패해도 추측 대신 durable state와 증거로 이어가게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 repository 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

현재 버전: **0.7.0**

> **저장소의 실제 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 10초 사용법

```text
처음 사용 → 저장소 URL + "이 저장소 Sloar로 개발해"
평소 작업 → 그냥 개발 요청
웹 UI 작업 → Sloar가 web-design-guidance를 repository 규칙 다음으로 자동 참고
Apple 느낌 요청 → 필요할 때만 apple-web-design 추가 적용
기존 세션 업그레이드 → "이 세션 Sloar 최신 버전으로 업그레이드하고 현재 작업 상태는 유지한 채 계속해"
채팅 이동 → "새 채팅으로 넘겨줘"
새 채팅 → Sloar가 준 Resume 문장 붙여넣기
답변이 계속 안 끝남 → 새 채팅에서 저장된 turn과 현재 repository를 확인해 takeover/replay
```

## 처음 쓰는 사람

설치 명령을 몰라도 현재 채팅이 안전한 repository write/execution capability를 가지고 있다면 다음처럼 시작하면 된다.

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<원하는 작업>
```

Agent는 기존 `AGENTS.md`와 repository 지침을 보존하고, 가능한 경우 stable Sloar를 durable하게 설치/복구한 뒤 repository identity를 다시 확인하고 작업한다. 실제 write capability가 없으면 설치됐다고 주장하지 않는다.

### 로컬/수동 fallback

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

First Run Wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

설치기는 Sloar 소유 marker block만 `AGENTS.md`에 추가하며 기존 repository 지침을 지우지 않는다.

## 0.7 핵심: 웹개발 디자인 가이드

0.7.0부터 일반적인 user-facing 웹 UI 작업에는 bundled companion인:

```text
.agents/skills/web-design-guidance/SKILL.md
```

를 사용할 수 있다.

이 companion은 특정 유행 스타일을 강제하는 템플릿이 아니다. 우선순위는 항상:

```text
사용자가 직접 준 디자인 요구
> repository의 design system / brand / product 규칙
> 이미 배포된 UI, tokens, components, assets
> Sloar web-design-guidance fallback
```

이다.

즉 기존 제품이 이미 명확한 디자인 언어를 가지고 있으면 그걸 보존한다. `AI 느낌`, `요즘 스타일` 같은 이유로 전체 화면을 임의로 purple gradient, glass, bento card로 바꾸지 않는다.

### Design Read

새 화면이나 큰 redesign에서는 필요한 경우 다음 정도만 짧게 정리한다.

```text
surface: product | dashboard | landing | auth/onboarding | settings | content | commerce | other
primary user job:
visual tone:
density: compact | balanced | spacious
existing system to preserve:
signature decision:
responsive risk:
interaction/state risk:
```

사용자 prompt와 repository가 이미 충분한 답을 주면 별도 질문 없이 추론하고 진행한다.

### 기본적으로 보는 것

- 기존 design tokens, typography, spacing, radius, shadows, icon system
- user journey와 information hierarchy
- landing/dashboard/auth/settings/content/commerce 등 surface 특성
- mobile/tablet/desktop responsive behavior
- long text, chip, badge, table, URL/ID overflow
- hover/pressed/focus/loading/empty/error/selected 같은 실제 states
- keyboard/touch/accessibility
- motion이 실제 causality/continuity를 설명하는지
- 흔한 generated UI 패턴을 무의식적으로 반복하는지

### 흔한 AI UI를 자동으로 정답 취급하지 않음

다음은 금지 목록이 아니라 **맥락 없이 자동 선택하지 말라는 anti-pattern check**다.

- 모든 landing을 `왼쪽 텍스트 + 오른쪽 장식 카드` hero로 만드는 것
- 이유 없는 보라/핑크 AI glow gradient
- 내용 구조와 상관없는 bento/card 남발
- 모든 section에 큰 rounded rectangle
- hierarchy가 아닌 장식용 glassmorphism
- 의미 없는 floating blob/sparkle/fake chart
- 기존 icon system 대신 emoji 사용
- dense product UI에서 과도한 hero whitespace
- 모든 제목/CTA를 중앙 정렬
- 모든 element에 개별 entrance animation

제품/사용자 요구가 정당화하면 당연히 사용할 수 있다.

### Visual verification

웹 UI에 대해:

```text
build/compile GREEN != 시각적으로 정상
DOM geometry GREEN != hierarchy/spacing 정상
CSS 속성 존재 != 실제 렌더에서 읽기 좋음
```

브라우저/screenshot capability가 있다면 실제 rendered surface를 보고 visual claim을 해야 한다. responsive/state risk도 변경 범위에 맞게 확인한다.

브라우저가 없거나 provider가 막혔다면 그 범위를 `unverified` 또는 `PARTIAL`로 보고하고 **답변을 무한정 붙잡고 기다리지 않는다.** 0.6.1의 bounded terminalization 규칙이 그대로 적용된다.

### Apple 스타일은 별도 전문 companion

`apple-web-design`은 계속 포함되지만 일반 웹의 기본 디자인 언어는 아니다.

사용자가 Apple-like direct manipulation, interruptible motion, velocity-aware settling, translucent functional chrome 등을 명시적으로 원할 때만 일반 `web-design-guidance` 다음에 전문 companion으로 적용한다.

### 참고한 공개 프로젝트

0.7 companion은 다음 MIT-licensed 프로젝트들의 유용한 구조를 분석해 Sloar 방식으로 새로 일반화했다.

- `nextlevelbuilder/ui-ux-pro-max-skill` — product-aware design decision / style-color-type / anti-pattern 구조
- `superdesigndev/superdesign-skill` — repository-aware persistent design-system memory
- `educlopez/ui-craft` — surface recipe / acceptance bar / rendered self-review / anti-generic generated UI

외부 runtime dependency는 없고 코드를 통째로 vendor하지 않는다. 자세한 출처 메모는 `.agents/skills/web-design-guidance/NOTICE.md`에 있다.

## 기존 작업 세션 업그레이드

새 채팅을 만들 필요 없다.

```text
이 세션 Sloar 최신 버전으로 업그레이드하고 현재 작업 상태는 유지한 채 계속해.
```

정상적인 upgrade는:

```text
현재 repository identity 재확인
        ↓
설치된 Sloar 버전 확인
        ↓
현재 stable release 확인
        ↓
기존 Sloar core 백업
        ↓
Sloar core 업그레이드
        ↓
새 bundled companion이 없으면 추가
        ↓
기존 custom companion은 보존
        ↓
Sloar-owned AGENTS marker만 필요 시 갱신
        ↓
검증 + 최신 checkpoint/turn bridge
        ↓
원래 작업 계속
```

한다.

로컬 fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

기존 Sloar core는 `.git/sloar-upgrade-backups/` 아래에 백업된다. product source와 unrelated repository guidance를 초기화하지 않는다.

자세한 계약: [`.agents/skills/sloar-chat-coder/references/upgrading.md`](.agents/skills/sloar-chat-coder/references/upgrading.md)

## 답변이 끝나지 않는 문제

Sloar는 두 문제를 구분한다.

### 1. Agent self-extension

```text
RED → 하나만 더 로그 → 하나만 더 수정 → 하나만 더 검증 → ...
```

0.6.1부터 동일 failure fingerprint의 기본 corrective cycle은 bounded다.

```text
진단 1회
→ 그 진단에 대한 수정 최대 1회
→ 영향받은 검증 1회
```

같은 fingerprint가 그대로 실패하면 `PARTIAL`, `BLOCKED`, 또는 `FAILED`로 턴을 종료하고 사용자에게 결과를 돌려준다. `ULW`, `finish it`도 무한 retry/search/wait/polling 권한이 아니다.

정식 계약: [`.agents/skills/sloar-chat-coder/references/turn-terminalization.md`](.agents/skills/sloar-chat-coder/references/turn-terminalization.md)

### 2. Host 자체 stall

ChatGPT/app/server가 실제로 계속 `답변 중`인 채 delivery를 끝내지 못하는 경우 Sloar가 host spinner를 강제로 종료할 수는 없다.

대신 interruption-prone 작업에서:

```text
BEGIN_TURN -> ACTIVE -> bounded PROGRESS -> TERMINALIZE -> visible final response
```

를 사용해 engineering terminality와 response delivery를 분리한다.

- terminal turn 발견 → `TERMINAL_REPLAY_AVAILABLE`
- unterminated active turn 발견 → `ACTIVE_OR_INTERRUPTED`
- 새 채팅 takeover → fencing epoch 증가
- old session이 뒤늦게 살아나면 다음 guarded write에서 stale fence 확인

자세한 사용자 설명: [docs/INTERRUPTED_TURNS.ko.md](docs/INTERRUPTED_TURNS.ko.md)

정식 계약: [`.agents/skills/sloar-chat-coder/references/operational-continuity.md`](.agents/skills/sloar-chat-coder/references/operational-continuity.md)

## 새 채팅으로 이어가기

채팅이 길어졌을 때:

```text
새 채팅으로 넘겨줘.
```

권한이 있으면 기본 durable transport는 제품 branch와 분리된 sidecar다.

```text
branch: sloar/rollover-state

.sloar/rollover/
  latest.json
  checkpoints/
    <checkpoint-id>.json
```

새 채팅에는 보통:

```text
Resume the latest Sloar session for OWNER/REPO.
```

만 전달하면 된다.

Fresh chat은 checkpoint보다 먼저/current repository를 다시 검증하며, remote-only 환경에서 local worktree를 못 보면 `unobserved`로 남긴다. 영어 control sentence와 사용자-visible `response_language`는 별개다.

자세한 규칙: [`.agents/skills/sloar-chat-coder/references/chat-native-continuity.md`](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## Forge resilience

Git, GitHub/GitLab API, Actions/CI, permissions/policy는 같은 failure domain이 아니다.

```text
LOCAL_READY + REMOTE_DEGRADED
→ 로컬 IMPLEMENT/VERIFY 계속
→ publication만 보류

LOCAL_READY + REMOTE_PARTIAL
→ verified tree 보존
→ capability/identity/approval/policy 경로 변경
→ 같은 금지 operation 반복 금지
```

로컬 상태:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

bounded remote probe:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

기존 오류 분류:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

자세한 설명: [docs/FORGE_RESILIENCE.ko.md](docs/FORGE_RESILIENCE.ko.md)

## 핵심 모델

Repository work lifecycle:

```text
ONBOARD? -> RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

핵심 invariant:

```text
Repository identity = HEAD SHA + tree SHA + observable working-tree state
same failure + same inputs = change strategy
No evidence -> no completion claim
publication 직전 mutable remote state 재검증
```

필요한 프로젝트에서는 repository/verification/runtime anchor를 따로 관리한다.

Sloar는 framework, package manager, database, UI library, deploy provider 같은 제품 기술 선택을 대신하지 않는다. 대상 repository가 engineering/design method를 결정한다.

## 문서

- 처음 실행: [docs/FIRST_RUN.ko.md](docs/FIRST_RUN.ko.md)
- 연결/권한: [docs/CONNECTIONS.ko.md](docs/CONNECTIONS.ko.md)
- ChatGPT Plugin/App/Skill: [docs/CHATGPT_PLUGINS.ko.md](docs/CHATGPT_PLUGINS.ko.md)
- Forge resilience: [docs/FORGE_RESILIENCE.ko.md](docs/FORGE_RESILIENCE.ko.md)
- interrupted turn: [docs/INTERRUPTED_TURNS.ko.md](docs/INTERRUPTED_TURNS.ko.md)
- 일반 웹 디자인 companion: [`.agents/skills/web-design-guidance/SKILL.md`](.agents/skills/web-design-guidance/SKILL.md)
- Apple 전문 companion: [`.agents/skills/apple-web-design/SKILL.md`](.agents/skills/apple-web-design/SKILL.md)

## License

MIT. [LICENSE](LICENSE)
