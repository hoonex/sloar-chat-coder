# Sloar Chat Coder 사용자 가이드

이 문서는 Sloar 내부 구조를 몰라도 **처음 시작 → 평소 개발 → 업데이트 → 새 채팅 이동 → 멈춘 응답 복구**까지 할 수 있도록 만든 사용자용 가이드다.

현재 stable: **0.8.0**

## 1. 처음 시작하기

새 ChatGPT/Codex 채팅을 열고 아래 문장을 그대로 복사한 뒤 `OWNER/REPO`와 작업 내용만 바꾼다.

```text
다음 Sloar Chat Coder를 사용해서 이 저장소를 개발해.
Sloar: https://github.com/hoonex/sloar-chat-coder

대상 저장소:
https://github.com/OWNER/REPO

원하는 작업:
<여기에 만들거나 수정하고 싶은 내용을 적기>

먼저 Sloar 사용법과 현재 저장소 상태를 확인한 뒤 진행해.
```

Sloar를 처음 보는 채팅에서도 원본 저장소 링크를 같이 주므로, 이름만 보고 추측하지 않고 현재 문서를 읽고 시작할 수 있다.

### 새 저장소가 아직 없다면

먼저 빈 GitHub 저장소를 만든 뒤 위 문장에서 대상 저장소 URL만 넣으면 된다.

### 이미 Sloar가 설치된 저장소라면

더 짧게 말해도 된다.

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<원하는 작업>
```

## 2. 평소에는 그냥 작업을 요청하면 됨

한 번 Sloar가 설치되고 현재 세션이 저장소를 확인한 뒤에는 매번 Sloar 링크를 붙일 필요가 없다.

예:

```text
로그인 화면 모바일 레이아웃 수정해줘.
```

```text
이 오류 원인 찾고 고쳐줘. 테스트까지 해줘.
```

```text
새 기능 구현하고 PR까지 만들어줘.
```

Sloar는 저장소의 현재 상태를 대화 기억보다 우선해서 확인하고, 필요한 구현/검증/게시 단계를 진행한다.

## 3. 모호한 웹사이트 요청도 가능

사용자가 디자인 용어를 몰라도 된다.

예:

```text
친구들이 같이 여행 계획을 짜는 웹을 만들고 싶어.
모바일에서 편하고 세련됐으면 좋겠는데 디자인은 잘 모르겠어.
```

요청이 충분히 명확하면 바로 진행하고, 큰 방향을 잘못 고르면 재작업이 큰 경우에만 필요한 질문을 한다.

질문은 보통 이런 식이다.

```text
정보를 빨리 보는 게 더 중요해, 아니면 첫인상이 강한 게 더 중요해?
모바일이 주 사용 환경이야, PC도 동등하게 중요해?
차분하고 고급스러움 / 친근하고 부드러움 / 실험적이고 강렬함 중 어디에 가까워?
```

`glassmorphism`, `neumorphism`, `brutalism` 같은 용어를 사용자가 먼저 알 필요는 없다.

사용자가:

```text
알아서 제일 어울리게 해.
```

라고 하면 optional 디자인 질문을 계속하지 않고 제품 목적과 저장소 근거로 방향을 결정한다.

자세한 디자인 규칙:
- [web-design-guidance](../.agents/skills/web-design-guidance/SKILL.md)
- [Adaptive discovery](../.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](../.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](../.agents/skills/web-design-guidance/references/anti-ai-slop.md)

## 4. Sloar 업데이트

현재 작업 중인 채팅에서 그대로 말한다.

```text
이 세션 Sloar 최신 stable 버전으로 업그레이드하고,
현재 작업 상태는 유지한 채 계속해.
```

정상적인 업그레이드는 대략:

```text
현재 repository identity 재확인
→ 설치된 Sloar 버전 확인
→ 현재 stable 확인
→ 기존 Sloar 백업
→ Sloar-owned 파일만 업그레이드
→ bundled companion 확인
→ 테스트/검증
→ 현재 작업 계속
```

으로 진행된다.

제품 코드나 unrelated repository 지침을 초기화하는 방식이 아니다.

로컬 fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

자세한 계약: [upgrading.md](../.agents/skills/sloar-chat-coder/references/upgrading.md)

## 5. 채팅이 너무 길어졌을 때

기존 채팅에서:

```text
새 채팅으로 넘겨줘.
```

라고 한다.

Sloar가 durable rollover를 만들 수 있는 환경이면 현재 목표, 완료/진행/대기 작업, 중요한 결정, 검증 증거, 현재 저장소 identity와 다음 행동을 저장한다.

새 채팅에서는 Sloar가 준 Resume 문장을 붙여넣는다. 기본 형태는:

```text
Resume the latest Sloar session for OWNER/REPO.
```

이다.

새 채팅은 checkpoint를 무조건 믿지 않고 **현재 저장소 상태를 다시 확인한 뒤** 이어서 진행한다.

자세한 계약: [chat-native-continuity.md](../.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## 6. 답변이 계속 `답변 중`에서 멈춘 경우

두 경우를 구분한다.

### A. 에이전트가 계속 `하나만 더` 하며 끝내지 않는 경우

Sloar는 같은 실패를 무한 반복하지 않는다.

```text
진단
→ 필요한 수정 최대 1회
→ 영향받은 검증 재실행
```

후에도 같은 failure fingerprint가 남으면 `PARTIAL`, `BLOCKED`, `FAILED` 중 맞는 상태로 그 턴을 끝내고 현재 결과를 보고해야 한다.

자세한 계약: [turn-terminalization.md](../.agents/skills/sloar-chat-coder/references/turn-terminalization.md)

### B. ChatGPT/app/server 자체가 멈춘 경우

Sloar가 앱의 spinner를 강제로 종료할 수는 없다.

새 채팅에서 다음처럼 요청한다.

```text
이전 Sloar 작업이 답변 중에 멈춘 것 같아.
저장된 turn 상태와 현재 저장소를 확인해서 이어서 진행해.
```

이전 작업이 이미 terminal 상태면 완료 결과를 다시 보고하고, 중간에 끊겼다면 현재 저장소를 재확인한 뒤 takeover 흐름으로 이어간다.

사용자 설명: [INTERRUPTED_TURNS.ko.md](INTERRUPTED_TURNS.ko.md)

## 7. Sloar가 전체적으로 어떻게 작동하나

사용자가 외워야 하는 상태 머신은 아니지만, 내부 흐름은 대략 다음과 같다.

```text
ONBOARD?
→ RECOVER
→ IDENTIFY
→ MATERIALIZE
→ BRANCH
→ IMPLEMENT
→ VERIFY
→ PUBLISH
→ REMOTE_VERIFY
→ CLEANUP
```

핵심 원칙은 네 가지다.

```text
현재 저장소 실제 상태 > 채팅 기억
수정 전에 정확한 source identity 확인
같은 실패 + 같은 입력이면 같은 retry를 반복하지 않음
검증 증거가 없는 성공은 성공이라고 보고하지 않음
```

GitHub/CI/권한 문제가 있더라도 로컬 구현이 가능한지, publication만 막힌 것인지 등을 분리해서 판단한다.

## 8. 처음 설치가 자동으로 안 되는 경우

현재 ChatGPT/Codex 환경에 GitHub write나 code execution 권한이 없을 수 있다. 그 경우 Sloar는 설치됐다고 가장하면 안 된다.

로컬 설치:

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

상태 확인:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

연결/권한 설명: [CONNECTIONS.ko.md](CONNECTIONS.ko.md)

## 9. 가장 자주 쓰는 문장만 모아보기

```text
# 처음 사용
다음 Sloar Chat Coder를 사용해서 이 저장소를 개발해.
Sloar: https://github.com/hoonex/sloar-chat-coder
대상 저장소: https://github.com/OWNER/REPO
원하는 작업: <작업>
먼저 Sloar 사용법과 현재 저장소 상태를 확인한 뒤 진행해.

# 이미 설치된 저장소
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO
<작업>

# 업데이트
이 세션 Sloar 최신 stable 버전으로 업그레이드하고 현재 작업 상태는 유지한 채 계속해.

# 새 채팅 이동
새 채팅으로 넘겨줘.

# 멈춘 작업 복구
이전 Sloar 작업이 답변 중에 멈춘 것 같아. 저장된 turn 상태와 현재 저장소를 확인해서 이어서 진행해.
```

## 더 자세한 문서

- [FIRST_RUN.ko.md](FIRST_RUN.ko.md) — 첫 실행
- [CONNECTIONS.ko.md](CONNECTIONS.ko.md) — GitHub/외부 연결과 권한
- [CHATGPT_PLUGINS.ko.md](CHATGPT_PLUGINS.ko.md) — Plugin/App/Skill 차이
- [FORGE_RESILIENCE.ko.md](FORGE_RESILIENCE.ko.md) — GitHub/CI 장애와 권한 문제
- [INTERRUPTED_TURNS.ko.md](INTERRUPTED_TURNS.ko.md) — 멈춘 응답/새 채팅 복구
