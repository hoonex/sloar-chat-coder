# ChatGPT 플러그인, 앱, 그리고 Sloar

처음 쓰는 사람이 가장 헷갈리기 쉬운 **Plugin / App / Skill** 차이를 정리한 문서다.

## 현재 구조

Sloar 0.3.0 기준(2026-08-20), OpenAI는 ChatGPT와 Codex에서 워크플로 기능을 찾는 기본 위치를 Plugin Directory로 설명한다. 하나의 Plugin에는 Skill, App, App template이 포함될 수 있다. App은 외부 데이터와 실제 작업에 연결되는 인증 통합이다.

공식 문서:

- https://help.openai.com/ko-kr/articles/20001256-plugins-in-codex

실제 사용 가능 여부는 요금제, 워크스페이스 정책, 역할, 사용하는 화면, 지역, 포함된 앱의 기능에 따라 달라질 수 있다. UI가 바뀌면 이 문서의 오래된 메뉴 이름보다 최신 OpenAI 공식 문서를 우선한다.

## Sloar는 어디에 속하나

현재 Sloar Chat Coder는 GitHub에서 배포하는 **Agent Skill 저장소**다. **현재 Plugin Directory에 등록된 공식 Sloar 플러그인이라고 주장하지 않는다.**

- Sloar Skill: 저장소 개발 절차와 지침
- GitHub App/연결: 현재 채팅 환경에 노출된 경우 GitHub 데이터/작업을 인증해서 제공
- Plugin: Skill과 하나 이상의 App을 묶을 수 있는 발견/워크플로 패키지

따라서 다음은 서로 다른 일이다.

- Sloar를 설치했다고 GitHub 권한이 생기지 않는다.
- GitHub를 연결했다고 대상 저장소에 Sloar가 자동 설치되는 것도 아니다.
- GitHub 읽기가 된다고 쓰기 권한까지 증명된 것은 아니다.
- 로컬 `gh` 로그인이 되어 있어도 ChatGPT의 GitHub App 연결과는 별개다.

## 초보자용 선택표

1. **로컬에서 AI/터미널로 코딩만 하고 싶다.** 저장소에 Sloar Skill만 설치하면 된다. Hosted GitHub App이 필수는 아니다.
2. **ChatGPT/Codex가 GitHub를 직접 읽게 하고 싶다.** 지원되는 환경에서 현재 Plugin Directory/App 연결 절차를 사용하고 필요한 저장소만 권한을 준 뒤 agent가 실제 읽기 가능 여부를 확인하게 한다.
3. **branch/PR push나 CI 확인까지 맡기고 싶다.** 현재 환경에 해당 쓰기/CI 기능이 실제 노출되고 인증되어 있는지 agent가 따로 증명해야 한다.
4. **관련 Plugin/App이 안 보인다.** 요금제/워크스페이스/역할/화면/지역 제한일 수 있다. 작업에 충분하다면 local/sandbox 경로를 사용하고 불필요한 설정을 강요하지 않는다.

## 향후 Sloar Plugin

나중에 Sloar를 Plugin 형태로 배포하기 쉽게 구조를 확장할 수는 있지만 핵심 규칙은 유지한다. 외부 작업 권한은 명시적인 App 권한 뒤에 두고, Sloar는 항상 현재 환경에서 실제 가능한 기능을 확인한다.
