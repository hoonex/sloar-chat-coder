# Sloar 처음 사용 가이드

이 문서는 GitHub 연결, ChatGPT 플러그인, Agent Skill 같은 말을 처음 접하는 사람을 기준으로 한다.

## 가장 짧은 시작 방법

1. 이 Sloar 저장소를 받는다.
2. `install.py --target <내 프로젝트>`를 실행한다.
3. 작업할 프로젝트를 ChatGPT/Codex/다른 코딩 에이전트에서 연다.
4. “Sloar first-run capability check를 먼저 해”라고 요청한다.
5. Sloar가 지금 환경에서 가능한 가장 낮은 capability 경로를 선택하게 둔다.

GitHub 플러그인이 없어도 로컬/샌드박스 코딩은 가능하다. ChatGPT 안에서 GitHub 저장소 읽기/쓰기, 브랜치, PR, CI 로그, artifact까지 직접 다루고 싶을 때 GitHub App 연결이 특히 유용하다.

## ChatGPT 세팅

### 먼저 용어부터

- **Plugin**: 특정 작업을 쉽게 찾고 사용할 수 있게 묶은 워크플로 패키지. Skill과 App 등을 포함할 수 있다.
- **App**: GitHub 같은 외부 서비스에 로그인/권한을 연결해서 실제 데이터와 동작을 제공한다.
- **Skill**: AI가 따라야 할 재사용 가능한 작업 절차다.

Sloar의 핵심은 **Skill**이다. GitHub 저장소 접근 권한은 사용 가능한 경우 **GitHub App**이 제공한다. 나중에 Sloar 자체가 Plugin Directory에 배포되더라도 이 구분은 그대로다.

### GitHub 연결이 필요할 때

지원되는 ChatGPT 환경에서는 보통 다음 흐름이다.

1. Plugin Directory 또는 `Settings -> Plugins`를 연다.
2. GitHub 관련 기능을 선택하고 필요한 App을 확인한다.
3. Connect가 가능하면 OAuth 연결을 진행한다.
4. GitHub에서 ChatGPT가 접근해도 되는 저장소만 선택한다.
5. ChatGPT로 돌아와 저장소가 보이는지 확인한다.

플랜, 워크스페이스 정책, 역할, 지역, 현재 사용하는 ChatGPT 화면에 따라 가능 여부가 달라질 수 있고, 관리자에 의해 App이 비활성화될 수도 있다. 그래서 Sloar는 메뉴가 “원래 있어야 한다”고 가정하지 않고 **현재 실제 도구를 증거로 사용한다.**

Sloar 0.2.0 작성 시점 공식 참고 문서:

- https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex
- https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

나중에 ChatGPT UI가 바뀌면 이 문서의 오래된 메뉴 이름보다 최신 OpenAI 공식 안내를 우선한다.

## 첫 실행 때 AI가 확인해야 하는 것

```text
Surface: ChatGPT / Codex / 기타 / 알 수 없음
Execution: 가능 / 불가능
Repository read: 어떤 경로로 가능한지
Repository write: 어떤 경로로 가능한지
PR + CI: 가능한지
Web: 가능한지
Best starting level: L0..L5
현재 요청을 막는 실제 누락 설정: 무엇인지
```

그리고 다음을 구분해야 한다.

- **not installed**: 필요한 기능 자체가 설치되지 않음
- **not authorized**: 연결은 있으나 권한이 없음
- **not exposed on this surface**: 현재 ChatGPT 화면에서 기능이 제공되지 않음
- **not needed**: 없어도 지금 작업에는 문제 없음

처음 쓰는 사람에게 필요하지도 않은 플러그인을 전부 설치하라고 시키면 안 된다.

## GitHub가 연결되지 않았다면

Sloar는 멈추는 대신 낮은 단계로 내려간다.

- 로컬/샌드박스 clone 사용
- 업로드된 zip/bundle 사용
- push 대신 검증된 patch/diff 생성
- 구현/테스트는 끝났지만 “게시만 막힘”인지 정확히 구분

## 설치 명령

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target ../my-project
```

옵션:

```text
--dry-run       실제 수정 없이 결과 미리보기
--no-agents     대상 AGENTS.md는 건드리지 않음
--force         기존 Sloar skill 디렉터리를 교체
```

## 로컬 진단

```bash
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py .
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py . --json
```

`doctor.py`는 로컬 파일/터미널 쪽만 검사한다. 사용자의 ChatGPT 계정이나 연결된 Plugin을 추측하지 않는다.

## 바로 복붙할 프롬프트

[examples/first-prompt.md](../examples/first-prompt.md)를 참고하면 된다.
