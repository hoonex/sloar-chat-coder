# Sloar Chat Coder

**대화가 끊겨도 개발 상태는 끊기지 않게. 처음 쓰는 사람도 시작점부터 알 수 있게.**

Sloar Chat Coder는 ChatGPT, Codex 및 Agent Skills를 읽을 수 있는 채팅 기반 개발 환경에서 저장소 작업을 더 정확하고 복구 가능하게 만드는 실행 프로토콜이다.

0.2.0부터는 기존의 복구/검증 규칙에 더해 **처음 설치하는 사람이 무엇을 연결해야 하는지, 지금 환경에서 무엇이 가능한지, 다음에 무엇을 해야 하는지**까지 다룬다.

> **저장소의 정확한 상태와 검증 증거가 채팅 기억보다 항상 우선한다.**

## 처음 쓰는 사람: 이것만 하면 됨

### 1. Sloar를 작업할 프로젝트에 설치

Sloar 저장소를 받은 뒤:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

이 스크립트는 대상 프로젝트에 `.agents/skills/sloar-chat-coder/`를 복사하고, 기존 내용을 지우지 않으면서 루트 `AGENTS.md`에 Sloar 진입 문구를 추가한다. 같은 명령을 다시 실행해도 동일 블록이 중복되지 않는다.

먼저 결과만 보고 싶으면 `--dry-run`을 사용한다.

### 2. 로컬 환경 진단

대상 프로젝트에서:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py .
```

Git 작업트리인지, 현재 HEAD/tree가 무엇인지, 수정 파일이 있는지, Python/Node/GitHub CLI가 있는지, Sloar가 제대로 설치됐는지 보여준다.

단, 이 스크립트는 **사용자의 ChatGPT 계정에 어떤 플러그인이 연결돼 있는지**까지 볼 수 없다. 그 부분은 Sloar의 agent-side 첫 실행 규칙이 현재 채팅의 실제 도구 목록을 보고 판단한다.

### 3. 첫 프롬프트

```text
이 저장소에서 Sloar Chat Coder를 사용해. 아무것도 수정하기 전에 first-run capability check를 하고, 정확한 저장소 상태를 복구한 다음 작업을 진행해.
```

더 자세한 입문 안내: [docs/FIRST_RUN.ko.md](docs/FIRST_RUN.ko.md)

## ChatGPT에서 Plugin / App / Skill 차이

여기가 처음 쓰는 사람한테 가장 헷갈리는 부분이다.

- **Skill**: AI가 어떤 절차로 일할지 알려주는 재사용 가능한 지침. Sloar의 핵심이 여기에 해당한다.
- **App**: GitHub 같은 외부 서비스에 인증하고 실제 데이터/동작 권한을 제공하는 연결 계층.
- **Plugin**: 특정 워크플로를 위해 Skill과 App 등을 묶어 배포/발견하기 쉽게 만든 패키지.

즉 **Sloar Skill을 설치했다고 GitHub 권한이 자동으로 생기는 게 아니다.** 반대로 GitHub App이 연결돼 있다고 Sloar 규칙이 자동 적용되는 것도 아니다.

현재 ChatGPT에서는 Plugin Directory가 워크플로 기능을 찾는 중심 위치이고, 플러그인이 필요한 App을 포함하거나 의존할 수 있다. GitHub 같은 외부 접근은 underlying App의 연결/권한에 따라 결정된다. 플랜, 워크스페이스 정책, 역할, 지역, 사용 중인 ChatGPT 화면에 따라 사용할 수 있는 기능은 다를 수 있으므로 **Sloar는 항상 실제 도구를 보고 판단한다.**

### ChatGPT + GitHub를 처음 세팅한다면

1. ChatGPT의 Plugin Directory 또는 Settings의 Plugins에서 GitHub 관련 기능을 확인한다.
2. GitHub App 연결이 필요하면 Connect/OAuth를 완료한다.
3. ChatGPT가 접근해도 되는 저장소만 선택한다.
4. 연결 후에도 Sloar는 실제로 read/write/PR/CI 로그 같은 기능이 있는지 다시 확인한다.
5. 쓰기 권한이 없더라도 멈추지 않는다. 로컬/샌드박스에서 구현하고 patch/zip/PR-ready 산출물로 낮은 capability 경로를 사용한다.

**중요:** Sloar는 사용자에게 없는 플러그인이나 권한을 있다고 가정하지 않는다.

## 첫 실행에서 Sloar가 확인할 것

Sloar 0.2.0은 처음 보는 환경에서 다음을 간단히 분류한다.

```text
execution: sandbox / terminal / none
repository read: native git / GitHub app / manual
repository write: native git / GitHub app / none
web: available / unavailable
CI/log access: available / unavailable
artifact transport: available / unavailable
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

플러그인이 없다는 이유만으로 L5가 되는 것은 아니다. 예를 들어 GitHub 쓰기 기능이 없어도 로컬 코딩과 검증이 가능하면 거기까지 진행하고 정확한 patch를 만들 수 있다.

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

`ONBOARD`는 초보자용 설정/능력 확인 단계이지 매 작업마다 길게 설명하는 단계가 아니다. 환경이 이미 알려져 있으면 생략하거나 아주 짧게 끝낸다.

## 핵심 차별점

### Repository Identity Contract

```text
identity = HEAD SHA + tree SHA + working-tree state
```

### Capability Ladder

항상 가장 낮은 충분 단계부터 사용한다.

### Failure Fingerprint

```text
same failure + same inputs = change strategy
```

### Evidence Ledger

```text
No evidence -> no completion claim.
```

### Publication Guard

게시 직전 remote base/head를 다시 확인해 동시 작업을 덮어쓰지 않는다.

## 원칙

Sloar는 프로젝트의 기술 선택을 대신하지 않는다. 프레임워크, 테스트 도구, 배포 방식, DB, 패키지 매니저 등은 항상 대상 저장소가 결정한다. Sloar는 **연속성, 정확성, 온보딩, 실패 처리, 동시성, 게시 안전성, 증거**만 담당한다.

버전: **0.2.0**
