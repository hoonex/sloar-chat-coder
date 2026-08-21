# ChatGPT 연결 추천

Sloar 핵심 기능은 특정 ChatGPT Plugin/App을 필수로 요구하지 않습니다. 정확한 Git 작업트리와 코드 실행 환경만 있어도 로컬 구현·검증·복구 프로토콜을 사용할 수 있습니다.

다만 사용자가 ChatGPT/Codex에게 GitHub, 배포 플랫폼, DB 같은 **원격 서비스를 직접 조작하게 맡기고 싶다면 해당 연결이 필요**합니다. Sloar는 저장소의 실제 파일/원격 정보에서 필요한 연결을 추천하지만, **연결은 사용자가 직접 수행**하고 현재 채팅에서 실제 권한이 있는지는 agent가 다시 검증합니다.

## 연결 수준

### GitHub 원격 작업의 기본 연결

**GitHub** — 저장소 origin이 GitHub이고 ChatGPT/Codex에게 다음을 맡기고 싶다면 기본적으로 권장합니다.

- 원격 저장소 읽기/쓰기
- branch/commit 작업
- Pull Request 생성·검토
- GitHub Actions/CI 상태·로그 확인
- GitHub를 통한 publication

로컬에서만 Sloar를 쓸 때는 GitHub 연결이 필수가 아닙니다. 연결할 때는 agent가 실제로 작업해야 하는 저장소만 허용하는 것을 권장합니다.

또한 **GitHub 읽기가 된다고 모든 쓰기 권한이 있는 것은 아닙니다.** 일반 파일 수정은 가능해도 `.github/workflows/*` 수정 권한이 없을 수 있으므로 Sloar가 필요한 기능을 각각 확인합니다.

### 저장소에 따라 자동 권장되는 연결

First Run Wizard는 다음 흔적을 보고 관련 연결을 추천합니다.

| 연결 | 감지 기준 | 연결하면 좋은 작업 |
| --- | --- | --- |
| Vercel | `vercel.json`, `.vercel/project.json`, Vercel 패키지 흔적 | 프로젝트/배포/Production 상태 확인 및 배포 |
| Supabase | `supabase/`, Supabase SDK·dependency 흔적 | DB, Auth, migration, Edge Function, 프로젝트 상태 |
| Netlify | `netlify.toml`, `.netlify/`, Netlify 패키지 흔적 | 빌드·배포·프로젝트 관리 |
| OpenAI Platform | OpenAI SDK·dependency 흔적 | API key, 프로젝트 설정, OpenAI 기반 런타임 구성 |

이 추천은 "이 서비스가 현재 ChatGPT에 연결되어 있다"는 뜻이 아니며, 실제 production에서 사용 중이라는 증거도 아닙니다. 현재 플랜/워크스페이스/화면에서 해당 App/Plugin이 제공되는지도 별도로 확인해야 합니다.

## 사용자가 직접 연결하는 흐름

1. 대상 저장소에서 `python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .`를 실행합니다.
2. 기본 출력의 `Suggested connections`를 확인합니다. 자세한 정보는 `--json`의 `connections.items`에서 볼 수 있습니다.
3. ChatGPT/Codex의 현재 **Plugins / Apps / Connections** 화면에서 추천된 서비스 이름을 검색합니다.
4. **Connect**를 눌러 해당 서비스의 공식 인증 화면에서 직접 로그인합니다.
5. 작업에 필요한 최소 저장소/프로젝트 범위만 허용합니다.
6. 채팅으로 돌아와 agent가 read/write/PR/CI/deploy 기능을 실제로 사용할 수 있는지 검증하게 합니다.

Sloar는 연결을 위해 사용자에게 서비스 비밀번호, access token, service-role key, API secret을 채팅에 붙여넣으라고 요구하지 않습니다.

## 무엇이 필수인가

- **Sloar 핵심:** 외부 ChatGPT 연결 없음도 가능
- **GitHub 원격 개발 전체:** GitHub 연결을 사실상 기본 연결로 권장
- **배포/DB 작업:** 저장소에서 감지되고 실제 작업에 필요한 provider만 연결
- **연결이 없음:** 가능한 범위의 로컬 IMPLEMENT/VERIFY는 계속 진행하고, 이를 GitHub 장애 같은 `REMOTE_DEGRADED`로 잘못 분류하지 않음

## 부분 권한도 따로 처리

연결 자체는 되어 있어도 일부 작업만 막힐 수 있습니다. 예를 들어 GitHub App이 일반 repository file은 수정하지만 workflow file 수정에는 별도 `workflows` 권한이 필요할 수 있습니다.

이 경우 Sloar는 서비스 장애로 보지 않고 `REMOTE_PARTIAL`로 분류해서 **같은 요청을 반복하는 대신 권한/transport/게시 전략을 바꿉니다.**
