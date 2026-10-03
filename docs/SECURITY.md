# Security model

OpenAgent is designed to act on a real computer. Treat every tool as a privileged capability.

## Principles

### 1. The model does not own credentials

Passwords and long-lived secrets should never be copied into prompts, memory, logs, or Git.

The initial vault stores secrets through the operating-system credential store using `keyring`. SQLite stores only metadata and an opaque secret reference.

### 2. The harness owns actions

The model can request a tool call. The harness decides whether it is valid, allowed, and complete.

A future Sentinel layer will classify actions such as:

- read page: allow
- navigate browser: allow
- submit form: ask
- write file: ask or workspace policy
- delete file: always ask
- send email: ask
- commit code: ask
- merge/publish: always ask

### 3. Tool results are source of truth

OpenAgent must not report success until the underlying tool confirms success.

## Browser prompt injection

Web pages are untrusted input. Page content must not be allowed to redefine system instructions or permission policy.

The browser tool should separate:
- page text;
- tool metadata;
- trusted harness instructions.

## Public repository hygiene

Never commit:
- `.env`
- passwords
- OAuth tokens
- browser profiles
- SQLite runtime databases
- logs containing private data

The repository `.gitignore` excludes the default local runtime directories.

## Credential filling

The planned browser-login flow is:

1. the model asks whether a credential is available for a domain;
2. the harness returns only metadata / availability;
3. after permission checks, the harness retrieves the secret from the OS vault;
4. the browser tool fills the field directly;
5. the raw secret is not returned to the model.

## Local browser profile

The persistent browser profile contains sensitive session data and must remain local. It is excluded from Git.
