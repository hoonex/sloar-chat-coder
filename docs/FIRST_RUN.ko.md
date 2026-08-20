# Sloar 처음 사용 가이드

이 문서는 GitHub 연결, ChatGPT Plugin, Agent Skill 같은 말을 처음 접하는 사람을 기준으로 한다.

## 가장 짧은 시작 방법

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target ../my-project
python3 ../my-project/.agents/skills/sloar-chat-coder/scripts/wizard.py ../my-project
```

ZIP으로 받았다면 압축을 풀고 그 Sloar 폴더에서 같은 `install.py` 명령을 실행하면 된다.

그다음 대상 프로젝트를 ChatGPT/Codex/다른 코딩 agent에서 열고 이렇게 요청한다.

```text
이 저장소에서 Sloar Chat Coder를 사용해. 수정하기 전에 현재 채팅에서 실제 가능한 GitHub/CI/browser 기능을 확인하고, 정확한 저장소 상태를 복구한 뒤 작업을 시작해.
```

GitHub Plugin/App이 없어도 로컬/샌드박스 코딩 자체는 가능할 수 있다. ChatGPT 안에서 GitHub 저장소 읽기/쓰기, branch, PR, CI 로그, artifact를 직접 다룰 때는 현재 환경에 GitHub 관련 App 기능이 실제로 노출되고 인증되어 있어야 한다.

## First Run Wizard

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py . --json
```

기본 화면은 길게 설명하지 않는다.

```text
Sloar readiness
Repository: ready | missing | unknown
Sloar skill: ready | missing
Execution: ready | missing
GitHub read/write: unknown (agent check)
CI/browser: unknown (agent check)
Next: 한 가지 행동 또는 ready to work
```

`wizard.py`는 로컬 파일/터미널에서 증명할 수 있는 것만 확인한다. 사용자의 ChatGPT 계정이나 현재 채팅에 어떤 App/Plugin이 연결돼 있는지는 로컬에서 추측하지 않는다. 그 부분은 현재 agent가 실제 tool inventory를 확인해야 한다.

## ChatGPT의 Plugin / App / Skill

Sloar 0.3.0 작성 시점 OpenAI 공식 설명은 다음 구조다.

- **Plugin**: 워크플로를 발견하고 활성화하기 위한 패키지. Skill, App, App template 등을 포함할 수 있다.
- **App**: GitHub 같은 외부 데이터와 실제 작업에 연결되는 인증 통합.
- **Skill**: agent가 따라야 할 재사용 가능한 지침/워크플로.

현재 Plugin Directory가 ChatGPT와 Codex의 워크플로 기능을 찾는 기본 위치로 안내되고 있다. 실제 Plugin/App 사용 가능 여부는 플랜, 워크스페이스 정책, 역할, 화면, 지역, 포함된 App 기능에 따라 달라질 수 있다.

공식 문서:

- https://help.openai.com/ko-kr/articles/20001256-plugins-in-codex

자세한 구분은 [CHATGPT_PLUGINS.ko.md](CHATGPT_PLUGINS.ko.md)를 참고한다.

**현재 Sloar는 GitHub에서 배포하는 Agent Skill 저장소다. Plugin Directory에 등록된 Sloar Plugin이라고 주장하지 않는다.**

## GitHub 연결이 필요한 경우

ChatGPT/Codex가 GitHub를 직접 읽거나 쓰게 하고 싶다면:

1. 현재 Plugin Directory에서 GitHub 관련 workflow/app capability가 제공되는지 확인한다.
2. 필요한 App 연결과 인증을 완료하고 필요한 저장소에만 권한을 준다.
3. Sloar가 현재 채팅에서 실제 repository read/write/PR/CI 기능이 노출됐는지 다시 확인하게 한다.
4. read가 된다고 write까지 가능하다고 가정하지 않는다.

버튼이나 기능이 보이지 않는다면 요금제/워크스페이스/역할/표면/지역 제한일 수 있다. 작업에 필요하지 않다면 억지로 설정하지 않고 local/sandbox 경로를 사용한다.

## 설치 옵션

```text
--dry-run       실제 수정 없이 결과 미리보기
--no-agents     대상 AGENTS.md를 만들거나 수정하지 않음
--force         기존 Sloar skill 디렉터리를 새 버전으로 교체
```

installer는 기존과 다른 Sloar가 있을 때 `--force` 없이 조용히 덮어쓰지 않는다.

## Local doctor

```bash
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py .
python3 .agents/skills/sloar-chat-coder/scripts/doctor.py . --json
```

`doctor.py`는 HEAD/tree/dirty/origin, Git/Python/Node/npm/gh 여부, 로컬 `gh auth` 성공 여부 등을 진단한다. 이것도 ChatGPT 계정의 App/Plugin 상태를 대신하지 않는다.

## GitHub가 연결되지 않았다면

Sloar는 가능한 경우 멈추지 않고 낮은 capability 경로로 내려간다.

- 로컬/샌드박스 clone 사용
- 업로드된 zip/bundle 사용
- push 대신 검증된 patch/diff 생성
- 구현/테스트는 끝났고 게시만 막힌 상황을 구분

처음 쓰는 사람에게 지금 작업에 필요하지 않은 Plugin/App을 전부 설치하라고 시키지 않는 것이 원칙이다.

## 바로 복붙할 프롬프트

[examples/first-prompt.md](../examples/first-prompt.md)를 참고하면 된다.
