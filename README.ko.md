# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. 저장소가 움직이거나 도구가 실패해도 추측 대신 durable state와 증거로 이어가게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 repository 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

현재 버전: **0.8.0**

> **저장소의 실제 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 10초 사용법

```text
처음 사용 → 저장소 URL + "이 저장소 Sloar로 개발해"
평소 작업 → 그냥 개발 요청
모호한 웹 UI 요청 → 목적/사용자/느낌 중 정말 중요한 것만 필요한 만큼 질문
디자인 용어를 모름 → 일상적인 표현을 Design DNA로 번역해서 진행
"알아서 해" → optional 질문 중단하고 product/repository 근거로 결정
웹 UI 구현 후 → responsive/state/visual + Anti-AI-Slop 재검토
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

설치기는 Sloar 소유 marker block만 `AGENTS.md`에 추가/갱신하며 기존 repository 지침을 지우지 않는다.

## 0.8 핵심: 모호한 웹 요청을 알아서 구체화

0.8.0의 `web-design-guidance`는 사용자가 디자인 용어를 잘 모른다는 전제로 동작한다.

예를 들어:

```text
학교 시간표 웹 만들어줘
```

처럼 말했을 때 무조건 바로 generic dashboard를 만들지도 않고, 반대로 고정 질문 10개를 던지지도 않는다.

먼저 필요한 사실을:

```text
KNOWN     명확히 알려짐
INFERRED  repository/product 문맥으로 합리적으로 추론 가능
UNKNOWN   서로 다른 큰 방향이 여전히 가능
```

으로 본다.

그리고 질문 가치가 큰 것만 고른다.

```text
question value
≈ decision impact × uncertainty × rework cost
  ÷ reversibility
```

정확한 수학 공식이 아니라 판단 원칙이다. 나중에 쉽게 바꿀 수 있는 radius/shadow/spacing은 보통 묻지 않고, 화면 전체 구조가 달라질 수 있는 목적/주 사용자/주 플랫폼/정보 밀도/느낌은 필요하면 묻는다.

### 질문 개수도 고정하지 않음

대략적인 기본값은:

```text
요구가 거의 명확함 → 0개
작은 중요한 갈림길 하나 → 0~1개
방향은 있지만 몇 가지 큰 선택이 남음 → 1~3개
새 제품인데 목적/톤/플랫폼이 많이 모호함 → 2~4개
"간지나는 사이트 만들어줘" 수준 → 3~5개 핵심 질문을 한 번에
```

이다.

이 숫자는 quota가 아니다. 질문 하나가 여러 모호성을 해결하면 더 적게 묻는다. 질문을 하나씩 끝없이 이어가는 인터뷰 루프는 피한다.

### 디자인 용어 대신 사람이 답할 수 있게 물음

좋은 질문:

```text
정보를 빨리 훑는 게 중요해, 아니면 첫인상이 강한 게 중요해?
차분하고 고급스러움 / 친근하고 부드러움 / 실험적이고 강렬함 중 어디에 가까워?
버튼이나 카드가 눌리고 따라오는 손맛이 필요해, 아니면 움직임은 최소화할까?
모바일이 주 사용 환경이야, PC도 동등하게 중요해?
```

보통 피하는 질문:

```text
neumorphism vs glassmorphism?
brutalism vs neo-brutalism?
8px radius vs 12px radius?
```

사용자가 이미 그런 용어를 쓰는 경우에는 당연히 그대로 사용할 수 있다.

### 사용자가 `알아서`라고 하면

```text
알아서 제일 어울리게 해
```

라고 위임하면 optional 디자인 질문을 계속하지 않는다.

Product 목적, repository 디자인 근거, 기존 UI를 보고 합리적인 방향을 고른 뒤 중요한 가정만 남기고 진행한다.

### 말로 설명하기 어렵다면 2~3개 방향 후보

예:

```text
A. Calm Utility
   정보 우선, 절제된 색, 최소 motion

B. Soft Tactile
   부드러운 surface, 약한 translucency, 눌림/선택 손맛, 짧은 spring

C. Editorial Bold
   강한 typography, 비대칭 composition, 높은 시각적 임팩트
```

처럼 **경험이 실제로 다른 후보**를 보여주고 하나만 고르게 할 수 있다. 단순히 색만 다른 A/B/C는 의미가 없다.

정식 계약: [adaptive-design-discovery.md](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)

## 디자인은 한 단어가 아니라 여러 축의 조합

`Minimalism`, `Glassmorphism`, `Bento`, `Interactive`, `Spring`은 같은 종류의 선택지가 아니다.

Sloar 0.8은 필요할 때 디자인을 여러 축의 **Design DNA**로 본다.

```text
philosophy/tone
material language
composition
interaction language
motion posture
density
typography/color stance
```

예를 들어 같은 화면이 동시에:

```text
philosophy: soft minimal + functional
material: restrained translucency
composition: asymmetric compact grid
interaction: tactile + context-aware
motion: short spring
density: compact-balanced
```

일 수 있다.

지원되는 사고 범위에는 다음과 같은 것들이 있다.

```text
철학/톤
→ Functional, Minimalism, Maximalism, Editorial,
  Brutalism/Neo-brutalism, Refined/Luxury,
  Playful, Industrial/Technical, Organic, Retro, Futuristic/Spatial

Material
→ Flat, Skeuomorphic/Tactile, Soft UI/Neumorphism,
  Glassmorphism/Translucent, Clay/Soft-3D, Paper, Hard-surface

Composition
→ Grid, Asymmetric, Split, Full-bleed, Command center,
  Editorial, Bento, Timeline, Spatial layers, Single-focus

Interaction
→ Static, Microinteractive, Tactile, Direct manipulation,
  Gesture-driven, Scroll-driven, Context-aware/State-driven, Spatial

Motion
→ None, Restrained, Spring, Physics-based,
  Morphing, Cinematic, Parallax/Depth
```

이 목록을 한 화면에 다 넣는 게 목적이 아니다. **제품에 맞는 몇 축만 일관되게 선택**하고 `style soup`을 피한다.

정식 taxonomy: [design-taxonomy.md](.agents/skills/web-design-guidance/references/design-taxonomy.md)

## 0.8 핵심: AI 티 나는 UI를 종류별로 점검

`AI 티가 난다`는 것은 AI가 만들었다는 증명이 아니다. Sloar의 Anti-AI-Slop 검사는 **서로 다른 제품들이 아무 이유 없이 같은 생성형 기본값으로 수렴하는지**를 보는 디자인 감사다.

핵심 원칙:

> **금지 목록을 외우는 게 아니라, 자동 기본값을 제품에 맞는 의식적인 결정으로 교체한다.**

예를 들어 보라색, Inter, glass, bento, Lucide 자체는 잘못이 아니다. 제품/브랜드/기능상 이유가 있으면 그대로 쓰는 게 맞다.

### AI 티를 크게 나누면

```text
1. Palette / Material
2. Typography
3. Layout / Information Architecture
4. Components / Styling fingerprints
5. Interaction / State
6. Motion
7. Copy / Product evidence
8. Imagery / Fake data
9. Second-order defaults
```

대표적인 예:

- 이유 없는 purple/indigo AI palette, purple→blue gradient, gradient headline
- glass/blur/neon glow/aurora/blob를 공간적 이유 없이 장식으로 사용
- starter의 Inter/Geist/Roboto/system font를 아무 판단 없이 제품 전체 identity로 사용
- 반대로 AI 티를 피한다고 매번 Space Grotesk/Fraunces/Instrument Serif 같은 같은 `tasteful` 폰트로 교체
- `pill badge → centered H1 → generic subtitle → CTA 2개 → feature card 3개` SaaS hero
- 정보 hierarchy와 상관없는 bento
- `rounded-2xl shadow-lg` 류의 동일 card를 모든 곳에 반복
- icon을 전부 tinted rounded-square 안에 넣는 동일 treatment
- untouched shadcn/MUI/Bootstrap 등 component demo look
- fake 10k users / 99.9% / testimonials / logos / charts / activity data
- `Transform`, `Elevate`, `Unlock`, `Supercharge` 같은 제품 구체성이 없는 카피
- 모든 card hover lift, 모든 section fade-up scroll reveal
- default 화면만 있고 loading/empty/error/focus/pressed/selected 상태는 없는 UI
- 첫 cliché를 피한 뒤 매번 같은 `따뜻한 종이색 + serif`, `burnt orange`, `brutalist rescue`로 가는 **두 번째 기본값**

### P0 / P1 / P2

Finding은 필요할 때 이렇게 분류한다.

```text
P0 — 일반 사용자도 generic/generated 느낌을 받을 정도의 강한 tell
P1 — 디자이너/개발자가 쉽게 알아보는 template smell
P2 — polish/craft 부족
```

그리고 증거도 구분한다.

```text
CODE-CERTAIN
RENDER-CERTAIN
INFERRED
```

코드에서 `bg-gradient...`를 보는 것과, 실제 화면의 color dominance/spacing/hierarchy가 이상한지는 같은 종류의 증거가 아니다.

### 해결 방식

약한 해결:

```text
indigo → teal
Inter → Fraunces
rounded-2xl → rounded-md
```

강한 해결:

```text
제품 목적/사용자/Design DNA 재확인
→ composition/type/color/material/interaction을 한 방향으로 맞춤
→ 그 방향과 충돌하는 high-signal 기본값만 수정
→ 실제 렌더 재검토
```

즉 `AI 티 제거 스타일` 자체가 새로운 template이 되면 실패다.

정식 catalog/해결법: [anti-ai-slop.md](.agents/skills/web-design-guidance/references/anti-ai-slop.md)

## Visual verification

웹 UI에 대해:

```text
build/compile GREEN != 시각적으로 정상
DOM geometry GREEN != hierarchy/spacing 정상
anti-slop lint GREEN != 제품다운 디자인
CSS 속성 존재 != 실제 렌더에서 읽기 좋음
```

브라우저/screenshot capability가 있다면 실제 rendered surface를 보고 visual claim을 해야 한다. responsive/state risk와 P0/P1 anti-slop finding도 변경 범위에 맞게 재검토한다.

브라우저가 없거나 provider가 막혔다면 그 범위를 `unverified` 또는 `PARTIAL`로 보고하고 **답변을 무한정 붙잡고 기다리지 않는다.** 0.6.1의 bounded terminalization 규칙이 그대로 적용된다.

## Apple 스타일은 별도 전문 companion

`apple-web-design`은 계속 포함되지만 일반 웹의 기본 디자인 언어는 아니다.

사용자가 Apple-like direct manipulation, interruptible motion, velocity-aware settling, translucent functional chrome 등을 명시적으로 원할 때만 일반 `web-design-guidance` 다음에 전문 companion으로 적용한다.

## 참고한 공개 프로젝트

0.8 design guidance는 공개된 여러 design-agent/anti-slop 프로젝트의 유용한 구조를 분석해 Sloar 방식으로 독립적으로 일반화했다.

- `nextlevelbuilder/ui-ux-pro-max-skill` — product-aware style/color/type/anti-pattern 구조
- `superdesigndev/superdesign-skill` — repository-aware design-system memory
- `educlopez/ui-craft` — surface recipe / acceptance bar / rendered self-review
- `rwcod/anti-ai-slop-ui` — product-specific direction + common generated/default UI tell 감사
- `funboy322/avoid-ai-design` — P0/P1/P2, code-vs-render evidence, second-order-default 개념
- `imMamdouhaboammar/unslop-preflight` — vague request preflight / spec readiness 사고

외부 runtime dependency는 없고 외부 Skill을 그대로 vendor하지 않는다. 원본 repository/license가 각 원작의 기준이며 자세한 출처 메모는 `.agents/skills/web-design-guidance/NOTICE.md`에 있다.

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
기존 Sloar core 백업 + core 업그레이드
        ↓
새 bundled companion이 없으면 추가
        ↓
공식 untouched 구버전 companion이면 exact fingerprint 확인 후 백업/업그레이드
        ↓
수정된/custom companion은 그대로 보존
        ↓
Sloar-owned AGENTS marker만 필요 시 갱신
        ↓
검증 + 최신 checkpoint/turn bridge
        ↓
원래 작업 계속
```

한다.

특히 0.8은 공식 `web-design-guidance 0.7.0` fingerprint를 알고 있다.

```text
공식 untouched 0.7.0 → 안전하게 0.8.0으로 자동 migration
수정된 0.7.0 → 사용자 customization으로 판단하고 보존
```

버전 숫자가 낮다는 이유만으로 companion을 덮어쓰지 않는다.

로컬 fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

기존 Sloar core와 자동 migration되는 known companion은 `.git/sloar-upgrade-backups/` 아래에 백업된다. product source와 unrelated repository guidance를 초기화하지 않는다.

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
- Adaptive discovery: [adaptive-design-discovery.md](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- Design taxonomy: [design-taxonomy.md](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- Anti-AI-Slop: [anti-ai-slop.md](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- Apple 전문 companion: [`.agents/skills/apple-web-design/SKILL.md`](.agents/skills/apple-web-design/SKILL.md)

## License

MIT. [LICENSE](LICENSE)
