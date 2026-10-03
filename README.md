# OpenAgent

OpenAgent is a local-first, open-source personal agent harness: a ChatGPT/Muse-style desktop agent that runs on your computer, uses local models, can browse the web through your own connection, keeps long-lived memory, and executes tools through a permission layer.

The first model provider is **Qwen through Ollama**. The architecture is model-agnostic so other providers can be added later without rewriting the agent.

> Status: early foundation. The bootstrap/runtime, identity, memory store, credential vault abstraction, Qwen provider, agent modes, Ultra Think orchestration, browser tool, filesystem tool, and connector scaffolds are included. The full Tauri/React desktop UI is the next major milestone.

## Core ideas

- **Local-first** — the agent daemon, memory, chats, browser profile, workspaces, and logs live on your machine.
- **Model thinks, harness acts** — the LLM proposes structured actions; OpenAgent owns execution, permissions, persistence, and secrets.
- **Qwen first** — Ollama is the initial provider.
- **Plan Mode** — inspect and plan before acting.
- **Context-aware** — the runtime is designed for context metering and compaction without losing task state.
- **Persistent browser** — Playwright runs locally with a persistent browser profile, so traffic uses your normal local network connection.
- **Secrets stay out of prompts** — passwords are stored through the OS credential store; the model should only receive the fact that a credential exists.
- **Open by default** — MIT licensed.

## Reasoning modes

OpenAgent starts with five modes:

| Mode | Behavior |
| --- | --- |
| Instant | Single direct pass, minimal deliberation |
| Medium | Single agent with a short internal plan/review |
| High | Planner + execution + review |
| Max | Larger reasoning/tool budget and self-review |
| Ultra Think | Four logical Max agents working on one task through a shared blackboard, followed by synthesis |

**Plan Mode** is orthogonal to the reasoning mode. In Plan Mode, the agent is expected to inspect, research, and produce a runnable plan without making destructive changes.

## Quick start (Windows)

Open PowerShell:

```powershell
git clone https://github.com/DaMello/OpenAgent.git E:\Agent\OpenAgent
cd E:\Agent\OpenAgent
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

The bootstrap script:

1. creates a local virtual environment;
2. installs OpenAgent;
3. installs Chromium for the local browser tool;
4. creates the OpenAgent runtime directories;
5. initializes the SQLite database;
6. creates the default agent identity;
7. creates local credential metadata folders (actual secrets stay in the OS credential store).

Then verify the setup:

```powershell
.\.venv\Scripts\python.exe -m openagent doctor
```

Start a local Qwen chat:

```powershell
.\.venv\Scripts\python.exe -m openagent chat --mode high
```

Plan Mode:

```powershell
.\.venv\Scripts\python.exe -m openagent chat --mode max --plan
```

Ultra Think:

```powershell
.\.venv\Scripts\python.exe -m openagent chat --mode ultra
```

## Runtime layout

By default on Windows, if `E:\Agent` exists, OpenAgent uses it as its home. Override this with `OPENAGENT_HOME`.

```text
E:\Agent
├── OpenAgent\                 # Git repository
├── data\
│   └── openagent.db           # chats, messages, tasks, tool calls, metadata
├── memory\
│   ├── profile\
│   ├── episodes\
│   └── workspaces\
├── identity\
│   └── identity.md
├── models\
├── credentials\              # metadata only; passwords are NOT stored here
├── browser-profile\          # persistent local browser session
├── workspaces\
├── downloads\
├── cache\
├── logs\
└── runtime\
```

These runtime folders are intentionally excluded from Git.

## Configuration

Copy `.env.example` to your preferred environment configuration or set variables directly:

```text
OPENAGENT_HOME=E:\Agent
OPENAGENT_OLLAMA_URL=http://127.0.0.1:11434
OPENAGENT_MODEL=
OPENAGENT_CONTEXT_WINDOW=131072
OPENAGENT_AUTO_COMPACT_RATIO=0.75
```

If `OPENAGENT_MODEL` is blank, the Qwen provider asks Ollama for installed models and selects the first model whose name contains `qwen`.

## Browser

The browser tool uses Playwright with a **persistent local Chromium profile** stored in `browser-profile\`. It runs on your PC rather than in a cloud browser, so websites are accessed through your machine's network connection.

The browser tool is deliberately separate from the model. The harness decides which browser actions are allowed.

## Memory

The initial memory layer stores:

- **profile memory** — stable user/project preferences;
- **episodic memory** — notable past events and task outcomes;
- **workspace memory** — project-specific facts and decisions.

The current implementation uses SQLite with lightweight text search. Vector retrieval can be added later without changing the memory API.

## Credential vault

OpenAgent never commits credentials to Git.

The initial vault uses Python `keyring`, which maps to the operating system credential store on Windows. SQLite stores only metadata such as domain, username, and a secret reference.

Future browser login tools should receive a credential reference and let the harness fill fields directly, rather than placing raw passwords into the model context.

## Repository layout

```text
OpenAgent/
├── openagent/
│   ├── agent/                 # reasoning modes and orchestration
│   ├── connectors/            # Gmail, GitHub, future integrations
│   ├── providers/             # Qwen/Ollama first
│   ├── tools/                 # browser, filesystem, future computer use
│   ├── bootstrap.py
│   ├── config.py
│   ├── db.py
│   ├── identity.py
│   ├── memory.py
│   ├── paths.py
│   └── vault.py
├── apps/
│   └── desktop/               # Tauri + React UI target
├── docs/
│   ├── ARCHITECTURE.md
│   └── SECURITY.md
├── scripts/
│   └── bootstrap.ps1
├── .env.example
├── .gitignore
├── LICENSE
└── pyproject.toml
```

## Roadmap

### v0.1 — local agent core
- [x] Qwen/Ollama provider
- [x] runtime bootstrap
- [x] SQLite persistence
- [x] identity file
- [x] memory API
- [x] OS-backed credential vault abstraction
- [x] reasoning mode definitions
- [x] initial Ultra Think orchestration
- [x] local Playwright browser tool
- [x] filesystem tool
- [ ] permission/sentinel engine
- [ ] context meter + compaction checkpoints
- [ ] chat/task persistence wired into the agent loop
- [ ] Tauri + React desktop UI

### v0.2 — personal agent
- [ ] Gmail OAuth connector
- [ ] GitHub OAuth/device connector
- [ ] browser login through credential references
- [ ] background tasks
- [ ] task timeline and approvals UI

### v0.3 — Jarvis layer
- [ ] computer use / Windows UI Automation
- [ ] scheduler
- [ ] long-term semantic memory
- [ ] skills/plugins
- [ ] remote/mobile control

## Security model

OpenAgent is intended to operate on a real computer, so tools should be treated as privileged capabilities.

The project follows three rules:

1. **The model does not own credentials.**
2. **The model does not bypass the permission layer.**
3. **An action is not considered complete until the harness/tool confirms it.**

See [docs/SECURITY.md](docs/SECURITY.md).

## License

MIT.
