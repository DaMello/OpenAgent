# OpenAgent architecture

OpenAgent separates reasoning from execution.

```text
Desktop UI
    │
    ▼
Agent daemon / orchestrator
    ├── context + compaction
    ├── memory
    ├── task state
    ├── permissions / sentinel
    └── model router
            │
            ▼
         Qwen/Ollama

Tool layer
    ├── browser
    ├── filesystem
    ├── terminal (planned)
    ├── computer use (planned)
    ├── Gmail (planned)
    └── GitHub (planned)
```

## Model boundary

The model receives task context and tool schemas. It does not receive unrestricted operating-system access.

Tools execute in the harness. Permission checks belong between the model request and the tool execution.

## Memory

Memory is split into three scopes:

- profile
- episode
- workspace

The initial backend is SQLite. The API is intentionally simple so a vector store can be added later.

## Ultra Think

Ultra Think uses four logical agents sharing one model provider:

1. planner
2. builder
3. critic
4. reviewer

Round one runs in parallel. Their outputs become a shared blackboard. Round two lets each agent read the shared board and respond to the other agents' work. A final Max-mode synthesis produces the answer.

The agents are logical workers. OpenAgent does not load four separate model copies into VRAM.

## Browser

The browser runs locally via Playwright persistent Chromium.

This gives OpenAgent:
- a persistent browser profile;
- cookies/session continuity;
- visible headed browsing;
- network access through the user's own computer.

The future desktop UI will mirror browser state in a right-side Browser panel.

## Desktop UI target

The intended desktop app is Tauri + React, visually inspired by the Qwen Image Local interface:
- near-black dark theme;
- thin borders;
- small radii;
- state communicated with restrained color;
- compact monospace metadata;
- chat list on the left;
- conversation/composer in the center;
- Browser / Tasks / Files panel on the right.
