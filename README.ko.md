# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. GitHub가 흔들리거나 권한이 일부 부족해도 정확한 작업은 보존되게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 저장소 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

0.5.0은 기존 First Run/복구/Forge Resilience 위에 **Chat-native Continuity**를 추가한다. 처음 사용자가 저장소 URL만으로 Sloar를 시작할 수 있게 하고, 채팅이 길어졌을 때 durable checkpoint를 통해 새 채팅에서 바로 이어서 작업하게 한다.

> **저장소의 정확한 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 처음 쓰는 사람

### 권장: 채팅에서 바로 시작

현재 채팅에 안전한 repository write/execution capability가 있다면 사용자는 설치 명령을 몰라도 된다.

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<원하는 작업>
```

Agent는 현재 capability를 확인하고, 기존 저장소 지침을 보존하고, 가능한 경우 stable Sloar를 durable하게 설치/복구하고, 저장소 identity를 다시 확인한 뒤 실제 작업을 시작한다.

권한이 없는데 설치가 됐다고 주장하면 안 된다. durable bootstrap이 불가능할 때만 아래 로컬 설치 경로를 fallback으로 사용한다.

### 로컬/수동 fallback

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

대상 프로젝트에서 First Run Wizard도 계속 사용할 수 있다.

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

기존 `AGENTS.md` 내용을 지우지 않고 Sloar 진입 블록만 추가하며, 같은 설치를 다시 실행해도 블록이 중복되지 않는다.

## 0.5 핵심: 새 채팅으로 이어가기

평소에는 그냥 개발 요청을 하면 된다. 매번 `Sloar`를 붙일 필요가 없다.

채팅이 길어졌을 때:

```text
새 채팅으로 넘겨줘.
```

Sloar는 대화 전체를 복사하지 않고 다음 durable state만 압축한다.

```text
goal
completed
active
pending
decisions
evidence
blockers
next_action
response_language
observable repository identity
```

권한이 있으면 기본 durable transport는 별도 sidecar branch다.

```text
sloar/rollover-state

.sloar/rollover/
  latest.json
  checkpoints/
    <checkpoint-id>.json
```

제품 branch에는 runtime checkpoint를 섞지 않는다.

기존 채팅은 새 채팅용 control sentence 하나를 준다.

```text
Resume the latest Sloar session for OWNER/REPO.
```

새 채팅은 이전 대화를 다시 설명하라고 하기 전에 repository와 checkpoint를 읽고 현재 durable state를 재검증한다.

- 현재 observable identity가 checkpoint와 맞으면 `EXACT`
- observable HEAD/tree/branch 등이 움직였으면 `RECONCILE_REQUIRED`
- 로컬 working tree를 볼 수 없는 remote-only 채팅이면 `unobserved`라고 기록하고 clean으로 꾸며내지 않는다.

### 언어 연속성

영어 resume 문장은 control phrase일 뿐 사용자 대화 언어를 영어로 바꾸라는 뜻이 아니다.

Checkpoint에는 예를 들어 다음처럼 사용자-visible 응답 언어를 따로 저장할 수 있다.

```json
{
  "response_language": "ko-KR"
}
```

다만 ChatGPT 같은 host가 durable checkpoint를 읽기 전에 visible 진행 메시지를 강제할 수 있다. 그런 경우 Sloar는:

```text
PRE_RESPONSE_READ_BLOCKED
```

로 분류한다.

이 상태에서는 “checkpoint 덕분에 첫 응답부터 한국어가 됐다”고 증거 없이 주장하지 않고, 같은 host 조건에서 같은 테스트를 무작정 반복하지 않는다. Host가 silent durable read를 허용하거나 인증된 early language hint를 제공할 때만 differentiated validation을 다시 한다.

자세한 규칙: [`.agents/skills/sloar-chat-coder/references/chat-native-continuity.md`](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

### 로컬 checkpoint helper

```bash
python3 .agents/skills/sloar-chat-coder/scripts/session-rollover.py handoff . \
  --goal "설정 화면 마무리" \
  --active "desktop UI" \
  --next "browser regression 실행" \
  --response-language "ko-KR"
```

기본 로컬 상태는 `.git/sloar-rollover/`에 저장되므로 handoff 자체가 제품 working tree를 dirty하게 만들지 않는다.

## 0.4 핵심: Forge Resilience

Git 저장소와 GitHub/GitLab/Actions는 같은 장애 영역이 아니다.

원격 서비스 자체가 불안정하지만 로컬 source/tree와 검증은 정상이라면:

```text
LOCAL_READY + REMOTE_DEGRADED
= 구현/로컬 검증은 계속
= publication만 보류
```

GitHub 자체는 정상인데 현재 identity/정책으로 필요한 작업만 할 수 없다면:

```text
LOCAL_READY + REMOTE_PARTIAL
= 검증된 tree 보존
= 같은 권한으로 같은 요청 재시도 금지
= capability / identity / approval / policy 경로 변경
```

### 상태 확인

네트워크 없이 로컬 상태만:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

원격을 딱 한 번만 bounded probe:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

### 이미 발생한 오류 분류

네트워크 요청 없이 기존 로그를 읽는다.

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

대표적으로 다음을 구분한다.

- GitHub App이 일반 파일은 쓰지만 workflow 파일은 못 씀 → `CAPABILITY_MISMATCH / REMOTE_PARTIAL`
- CI `action_required`/승인 필요 → `REMOTE_ACTION_REQUIRED / REMOTE_PARTIAL`
- branch protection/ruleset → `POLICY_BLOCKED / REMOTE_PARTIAL`
- non-fast-forward/stale lease → `REMOTE_MOVED`, remote base 재확인 후 reconcile
- 429/5xx/DNS/timeout → `REMOTE_DEGRADED`

분류기는 raw error를 다시 출력하지 않고 class/layer/retry 전략/다음 행동과 SHA-256 fingerprint만 반환한다.

자세한 설명: [docs/FORGE_RESILIENCE.ko.md](docs/FORGE_RESILIENCE.ko.md)

## ChatGPT에서 Plugin / App / Skill 차이

- **Skill**: AI가 어떤 절차로 일할지 알려주는 재사용 가능한 지침. Sloar의 핵심.
- **App**: GitHub 같은 외부 서비스에 인증하고 실제 데이터/동작 권한을 제공하는 연결 계층.
- **Plugin**: 특정 워크플로를 위해 Skill과 App 등을 묶어 배포/발견하기 쉽게 만든 패키지.

**Sloar Skill을 설치했다고 GitHub 권한이 자동으로 생기는 게 아니다.** 반대로 GitHub App이 연결돼 있어도 read/write/workflow/merge/Actions 권한이 전부 같다고 가정하면 안 된다.

플랜, 워크스페이스 정책, 역할, 지역, 사용 중인 ChatGPT 화면에 따라 사용할 수 있는 기능은 다를 수 있으므로 Sloar는 항상 **현재 세션에서 실제 노출된 도구/권한과 실제 실패 증거**를 기준으로 판단한다.

## 첫 실행에서 Sloar가 확인할 것

```text
execution: sandbox / terminal / none
repository read: native git / GitHub app / manual
repository write: native git / GitHub app / none
web: available / unavailable
CI/log access: available / unavailable
artifact transport: available / unavailable
forge health/capability: healthy / partial / degraded / unknown
```

그리고 가능한 가장 낮은 capability level로 시작한다.

```text
L0 sandbox native
L1 sandbox acquisition
L2 connected repository transport
L3 supply mission
L4 bounded remote execution
L5 blocked
```

쓰기 권한이 없거나 workflow write만 막혀 있다는 이유로 로컬 구현까지 포기하지 않는다. 정확한 source가 있고 로컬 검증이 가능하면 거기까지 진행하고 durable patch/tree/checkpoint를 남긴다.

## 실행 상태 머신

```text
ONBOARD (필요할 때만)
  -> RECOVER
  -> IDENTIFY
  -> MATERIALIZE
  -> BRANCH
  -> IMPLEMENT
  -> VERIFY
  -> PUBLISH
  -> REMOTE_VERIFY
  -> CLEANUP
```

Forge 상태는 이 lifecycle 위에 별도로 겹친다.

```text
LOCAL_READY
REMOTE_HEALTHY | REMOTE_PARTIAL | REMOTE_DEGRADED
PUBLICATION_BLOCKED | ready
```

## 핵심 차별점

### Repository Identity Contract

```text
identity = HEAD SHA + tree SHA + working-tree state
```

### Capability Ladder

항상 가장 낮은 충분 단계부터 사용한다.

### Forge Capability Overlay

서비스 장애와 부분 권한/정책 문제를 분리한다.

### Failure Fingerprint

```text
same failure + same inputs = change strategy
```

### Evidence Ledger

```text
No evidence -> no completion claim.
```

### Publication Guard

게시 직전 remote base/head를 다시 확인해 동시 작업을 덮어쓰지 않는다. 장애나 권한 차단이 오래 지속된 뒤 publication할 때도 반드시 다시 확인한다.

## 원칙

Sloar는 프로젝트의 기술 선택을 대신하지 않는다. 프레임워크, 테스트 도구, 배포 방식, DB, 패키지 매니저 등은 항상 대상 저장소가 결정한다. Sloar는 **연속성, 정확성, 온보딩, 채팅 rollover, 실패 처리, 동시성, forge resilience, 게시 안전성, 증거**만 담당한다.

버전: **0.5.0**
