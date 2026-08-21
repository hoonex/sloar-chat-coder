# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. GitHub가 흔들리거나 권한이 일부 부족해도 정확한 로컬 작업은 보존되게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 저장소 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

0.4.0은 기존 First Run/복구/검증 규칙에 **Forge Resilience**를 추가한다. GitHub/GitLab/Actions 장애와 “서비스는 정상인데 현재 App/token에 특정 권한만 없음”을 구분하고, 같은 실패를 무작정 반복하지 않게 한다.

> **저장소의 정확한 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 처음 쓰는 사람: 4단계

### 1. Sloar 받기

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
```

ZIP으로 받아 압축을 풀어도 된다.

### 2. 작업 프로젝트에 설치

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

기존 `AGENTS.md` 내용을 지우지 않고 Sloar 진입 블록만 추가하며, 같은 설치를 다시 실행해도 블록이 중복되지 않는다.

### 3. First Run Wizard

대상 프로젝트에서:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

기본 결과는 Repository / Skill / Execution / GitHub·CI·browser 상태와 다음 행동 하나만 짧게 보여준다. ChatGPT의 App/Plugin 권한은 로컬에서 추측하지 않고 현재 agent가 실제 tool inventory를 확인한다. 전체 데이터가 필요하면 `--json`을 쓴다.

### 4. 첫 프롬프트

```text
이 저장소에서 Sloar Chat Coder를 사용해. 수정하기 전에 현재 채팅에서 실제 가능한 GitHub/CI/browser 기능을 확인하고, 정확한 저장소 상태를 복구한 뒤 작업을 시작해.
```

더 자세한 안내: [docs/FIRST_RUN.ko.md](docs/FIRST_RUN.ko.md), [docs/CHATGPT_PLUGINS.ko.md](docs/CHATGPT_PLUGINS.ko.md)

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

Sloar는 프로젝트의 기술 선택을 대신하지 않는다. 프레임워크, 테스트 도구, 배포 방식, DB, 패키지 매니저 등은 항상 대상 저장소가 결정한다. Sloar는 **연속성, 정확성, 온보딩, 실패 처리, 동시성, forge resilience, 게시 안전성, 증거**만 담당한다.

버전: **0.4.0**
