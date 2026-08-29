# First use — chat-native bootstrap

This experiment assumes the user may have **nothing Sloar-specific installed in the target repository yet**.

## Preferred first message

The user only needs the target repository and an ordinary request. Any language is allowed.

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<what I want you to build or fix>
```

A concise English equivalent is:

```text
Use Sloar for https://github.com/OWNER/REPO and continue with my request.
```

The user should not have to clone Sloar, run `install.py`, run the wizard, or understand Agent Skills before the first chat can begin **when the current chat has enough authorized repository and execution capability to bootstrap it safely**.

## What the agent does

On explicit first-use intent such as `Use Sloar`, the agent should:

1. Resolve the target repository and the capabilities actually available in the current chat.
2. Read the target repository's current `AGENTS.md` and check whether `.agents/skills/sloar-chat-coder/SKILL.md` already exists.
3. If Sloar is already installed, preserve the repository's existing installation and continue through normal Sloar recovery.
4. If it is absent and an authorized safe write path exists, obtain the documented stable Sloar core, install it without replacing unrelated `AGENTS.md` content, and verify the installed files before treating bootstrap as durable.
5. If durable write is unavailable, do not pretend Sloar was installed. The agent may use the public Sloar protocol ephemerally for the current chat, but must report that rollover persistence is unavailable until a durable path exists.
6. Resolve exact repository identity and relevant remote state.
7. Preserve the established user-facing response language independently from the language used in code, Git commands, agent protocol text, or later resume control phrases.
8. Begin the user's requested work. Do not turn a healthy bootstrap into a long setup tutorial.

## Expected visible response

Successful durable bootstrap should be short:

```text
Sloar ready.
Repository: OWNER/REPO
State: <short current state>

<start the requested work>
```

If the repository was already configured:

```text
Sloar restored.
Repository: OWNER/REPO
State: <short current state>

<continue the requested work>
```

These examples describe structure, not a forced output language. Visible responses should use the user's established response language.

If the chat cannot persist the bootstrap:

```text
Sloar can be used for this chat, but durable setup is unavailable with the current repository permissions.
I can continue locally/ephemerally; cross-chat rollover will not be claimed as durable.
```

Only then should the agent offer the smallest fallback needed, such as connecting repository write access or using the existing local installer.

## Local fallback only when required

If the environment cannot perform a durable chat-native bootstrap, the existing stable installer remains the fallback rather than the default onboarding experience:

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/project
```

The user should only see this path when the current chat genuinely lacks a safe installation capability.

## After first use

The user works normally. There is no requirement to prefix every request with Sloar.

```text
로그인 화면 만들어줘.
모바일 레이아웃도 고쳐줘.
테스트까지 해줘.
```

When the chat gets crowded, the user can simply say:

```text
새 채팅으로 넘겨줘.
```

The old chat prepares a durable rollover and returns one resume sentence:

```text
Resume the latest Sloar session for OWNER/REPO.
```

That English sentence is a **control phrase only**. It does not request an English conversation. The rollover checkpoint should preserve the established user-facing `response_language`, and the fresh chat should restore that language before its first visible reply.

The fresh chat re-resolves repository reality, loads the durable checkpoint, reconciles any movement, and continues without asking the user to reconstruct the old conversation.

## Design rule

The zero-setup experience is conditional on **actual capability**, not wishful automation.

- repository read only: Sloar may inspect and advise, but cannot claim durable installation;
- repository write available: bootstrap may be installed through an authorized safe path;
- execution available but remote write missing: local implementation may continue, publication/bootstrap durability remains blocked;
- no usable repository source: ask only for the missing repository source or access needed to proceed.

This keeps the first-use UX simple without weakening Sloar's evidence or authorization rules.
