# ChatGPT 플러그인, 앱, 그리고 Sloar

처음 쓰는 사람이 가장 헷갈리기 쉬운 **Plugin / App / Skill** 차이를 정리한 문서입니다.

## 현재 구조

Sloar는 세 계층을 분리해서 봅니다.

- **Skill**: AI가 어떤 절차로 일할지 알려주는 재사용 지침. Sloar 핵심이 여기에 해당합니다.
- **App/연결**: GitHub, Vercel, Supabase 같은 외부 서비스에 인증해서 실제 데이터와 작업 권한을 제공하는 계층입니다.
- **Plugin**: Skill과 App/연결을 묶거나 의존할 수 있는 워크플로 패키지입니다.

ChatGPT/Codex의 UI와 제공 여부는 플랜, 워크스페이스 정책, 역할, 화면, 지역에 따라 바뀔 수 있습니다. 오래된 메뉴명을 고정해서 가르치기보다 현재 Plugins / Apps / Connections 화면과 최신 제품 안내를 우선합니다.

## Sloar는 어디에 속하나

Sloar Chat Coder는 현재 GitHub에서 배포하는 **Agent Skill 저장소**입니다. Skill을 설치했다고 GitHub나 다른 외부 App이 자동 설치·인증됐다고 주장하지 않습니다.

따라서 다음은 서로 다른 일입니다.

- Sloar를 설치했다고 GitHub 권한이 생기지 않습니다.
- GitHub를 연결했다고 대상 저장소에 Sloar가 자동 설치되지 않습니다.
- GitHub 읽기가 된다고 쓰기/PR/Actions/workflow 파일 권한까지 증명된 것은 아닙니다.
- 로컬 `gh` 로그인과 ChatGPT의 GitHub 연결은 별개입니다.
- `vercel.json`이나 `supabase/`가 있다고 ChatGPT에 해당 서비스가 연결됐다고 볼 수 없습니다.

## 어떤 연결을 해야 하나

대상 저장소에서 First Run Wizard를 실행합니다.

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

이제 기본 출력의 `Suggested connections`에서 권장 연결을 보여주고, `--json`에서는 `connections.items`에 감지 이유와 권장 수준을 구조화해서 제공합니다.

기본 정책은 다음과 같습니다.

1. **로컬에서만 Sloar 사용** — 외부 ChatGPT 연결이 필수는 아닙니다.
2. **GitHub 원격 작업까지 맡기기** — origin이 GitHub이고 repo/branch/PR/CI/publication을 맡기고 싶다면 GitHub 연결을 기본 연결로 권장합니다.
3. **Vercel / Supabase / Netlify / OpenAI Platform** — 저장소에서 실제 흔적이 감지되고 요청한 작업에 필요할 때만 권장합니다.
4. **연결은 사용자가 직접 수행** — Sloar가 임의로 인증하거나 연결을 위해 비밀번호·토큰·service-role key를 채팅에 붙여넣으라고 요구하지 않습니다.
5. **연결 후 권한을 다시 검증** — App 연결은 부분 권한일 수 있습니다. 일반 GitHub 파일 수정은 가능해도 `.github/workflows/*`는 별도 권한 때문에 막힐 수 있습니다.

전체 추천표와 사용자 연결 흐름은 [CONNECTIONS.ko.md](CONNECTIONS.ko.md)를 참고하세요.

## 초보자용 선택표

1. **로컬에서 AI/터미널로 코딩만 하고 싶다.** Sloar Skill만 설치하면 됩니다.
2. **ChatGPT/Codex가 GitHub를 직접 다루게 하고 싶다.** GitHub를 사용자가 직접 연결하고 필요한 저장소만 허용한 뒤 agent가 실제 read/write/PR/CI 기능을 확인하게 합니다.
3. **프로젝트가 Vercel/Supabase/Netlify/OpenAI를 쓴다.** Wizard가 추천하고 실제 작업에 필요한 provider만 연결합니다.
4. **연결이 없거나 권한이 일부만 있다.** 가능한 로컬 작업은 계속 진행하며 이를 GitHub 장애 같은 `REMOTE_DEGRADED`로 잘못 분류하지 않습니다.

## 향후 Sloar Plugin

나중에 Sloar를 Plugin 형태로 묶더라도 핵심 원칙은 유지합니다. 외부 작업 권한은 사용자의 명시적인 App 연결 뒤에 두고, Sloar는 현재 세션에서 실제 가능한 기능을 확인한 뒤 사용합니다.
