# starxhub

**The Multi-Agent Development Team Configuration Center for Claude Code**

Spin up 23 specialized agents, 10 slash commands, guardrail hooks, and path-scoped rules with a single command — whether you're starting a new project from scratch or onboarding an existing one into a multi-agent workflow.

## Why starxhub

Every project has its own tech stack, business rules, and multi-tenant constraints. There's no "universal template" that fits all. starxhub generates a **project-specific starting point** tailored to your exact tech stack — not a "looks-usable-but-mismatches-everywhere" config.

## Two Skills, Full Project Lifecycle

| Skill | Purpose | Use Case |
|-------|---------|----------|
| **new-project** | Project scaffolding | Start from zero — generate a complete multi-agent team config |
| **onboard-project** | Existing project onboarding | Auto-detect tech stack and integrate into multi-agent workflow |

### new-project: Build from Scratch

```bash
/new-project /path/to/project --name "My Project" --backend python --frontend vue
```

What gets generated:

- **23 Specialized Agents** across 5 lifecycle phases (Requirements Analysis / Task Planning / Requirements Review / Development / Testing & Fixing)
  - 8 requirements review specialists (`req-*`) forming a complete review team
  - Plan gate duo: `plan-risk-analyst` (failure point scanning) + `plan-gatekeeper` (go/no-go decision)
  - Test & fix duo: `functional-tester` (test case design) + `bug-fixer` (5-step closed-loop fix)
- **11 Slash Commands** covering the full lifecycle from fuzzy idea to post-release retrospective
- **Guardrail Hooks** — pre-commit build+test checks, post-entity multi-tenant red-line scanning
- **Path-Scoped Rules** — auto-loaded conventions based on tech stack, injected when editing matching files

### onboard-project: Integrate Existing Projects

```bash
/onboard-project /path/to/existing-project
```

Auto-detects the tech stack, restructures directories, generates `.claude/` config and `CLAUDE.md`. Supports skeleton rules generation for unrecognized tech stacks.

## Supported Tech Stacks

| Dimension | Option | Description |
|-----------|--------|-------------|
| Backend | `dotnet` | .NET 8 + ASP.NET Core Web API + SqlSugar + MySQL |
| Backend | `python` | Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 |
| Frontend | `vue` | Vue 3 + Element Plus + Pinia + Vite + TypeScript |
| Frontend | `uniapp` | uni-app + Vue 3 + Pinia + TypeScript (H5 + WeChat Mini Program) |

When no tech stack is specified, the scaffold **prompts interactively** — it never silently defaults.

## Quick Start

### Installation

```bash
# Add the plugin marketplace
claude plugin marketplace add yangchun57/starxhub

# Install the plugin
claude plugin install starxhub@starxhub
```

### Usage

Invoke skills in Claude Code:

```bash
# Scaffold a new project
/new-project /path/to/project --name "E-Commerce System" --backend dotnet --frontend vue

# Onboard an existing project
/onboard-project /path/to/existing-project
```

Or run the script directly:

```bash
cd /path/to/plugin/skills/new-project/scripts
python scaffold.py /path/to/project --name "E-Commerce System" --backend dotnet --frontend vue
```

## Core Mechanisms

### Plan Gate

After the `architect` produces the architecture plan and before coding begins, `/new-feature` enforces a mandatory gate:

```
architect delivers → plan-risk-analyst scans (R1–R7 failure points) → plan-gatekeeper decides
                  ├─ PASS           → proceed to coding
                  ├─ CONDITIONAL    → confirm each condition, then proceed
                  └─ REJECT         → stop, return to architect for revision
```

Multi-tenant red-line violations are **absolute blockers** — no conditional pass. `/plan-gate` can also be used independently for existing projects.

### Path-Scoped Rules

Generated projects include a `.claude/rules/` directory with auto-loaded conventions:

```
.claude/rules/
├── workflow.md              # Always loaded: workflow conventions
├── database.md              # Always loaded: database & multi-tenant isolation rules
├── git.md                   # Always loaded: Git commit conventions
├── backend-api.md           # Auto-loaded when editing backend API files
├── backend-domain.md        # Auto-loaded when editing backend domain layer files
├── backend-infra.md         # Auto-loaded when editing backend infrastructure files
├── frontend-pages.md        # Auto-loaded when editing frontend page files
└── frontend-state.md        # Auto-loaded when editing frontend state/API layer files
```

Each rule file is under 50 lines of essential conventions, triggered automatically via `paths` glob matching. Full standards remain in `.claude/standards/` for deep reference.

## Project Structure

```
starxhub/                              # Repo root = plugin marketplace
├── .claude-plugin/marketplace.json   # Marketplace manifest
└── plugins/starxhub/                 # Plugin root (starxhub)
    ├── .claude-plugin/plugin.json     # Plugin manifest
    └── skills/
        ├── new-project/              # New project scaffolding skill
        │   ├── SKILL.md
        │   ├── scripts/
        │   │   ├── scaffold.py        # Main generator (renders by tech stack)
        │   │   └── split-standards.py # Standards splitter
        │   └── templates/
        │       ├── CLAUDE.md          # Project memory template (with placeholders)
        │       ├── .claude/
        │       │   ├── agents/        # 23 agent definitions
        │       │   ├── commands/      # 10 slash commands
        │       │   ├── hooks/         # Guardrail hook scripts
        │       │   ├── rules/         # Path-scoped rules
        │       │   ├── standards/     # Full standards documentation
        │       │   └── settings.json  # Permission config
        │       ├── code/              # Code project templates
        │       └── docs/              # Project documentation templates
        └── onboard-project/          # Existing project onboarding skill
            ├── SKILL.md
            └── scripts/
                └── detect_stack.py    # Tech stack detection script
```

## Notes

- **Placeholder rendering**: Template placeholders like `{{BACKEND_STACK}}`, `{{ENVELOPE}}`, etc. are rendered by `scaffold.py` based on the selected tech stack. See `BACKENDS[...]["tokens"]` and `FRONTS[...]["tokens"]` in `scaffold.py`.
- **Permission blacklist**: Rejects `git push`, destructive commands, `drop table`, `truncate table`, etc. Written to project-level `settings.json` by the generator.
- **Agent definitions are business-agnostic**: Project-specific red lines belong in each project's own `CLAUDE.md`.
- **Hook scripts**: Use `$CLAUDE_PROJECT_DIR` to locate the target project (defaults to `src/backend/api`).

## Changelog

### v2.1.0 — Rebrand: starxhub

- Plugin renamed: `multi-agent-scaffold` → `starxhub`
- Skills renamed:
  - `claude-code-multi-agent-scaffold` → `new-project`
  - `claude-code-project-onboard` → `onboard-project`
- New `onboard-project` skill: auto-detect tech stack and integrate existing projects into multi-agent workflow
- Directory restructured: `plugins/multi-agent-scaffold/` → `plugins/starxhub/`

### v2.0.0 — Lean Architecture + Path-Scoped Rules

- Added `.claude/rules/` path-scoped rules: 13 rule files auto-loaded by tech stack
  - Always-loaded rules (workflow/database/git)
  - Backend rules (backend-api/domain/infra) selected by `--backend dotnet|python`
  - Frontend rules (frontend-pages/state) selected by `--frontend vue|uniapp`
- Removed native agents/commands/hooks — only the scaffold generator skill remains
- Updated CLAUDE.md template to reference new rules auto-loading mechanism

### v1.4.0 — Plan Gate

- Added `plan-risk-analyst` (read-only, opus): R1–R7 failure point scanning with focus on multi-tenant red lines and AI-prone edge cases
- Added `plan-gatekeeper` (read-only, sonnet): C1 clarity / C2 completeness / C3 verifiability triple check, outputs PASS / CONDITIONAL / REJECT
- Added `/plan-gate` command for independent use on existing projects
- `/new-feature` now enforces a mandatory gate after architect delivery and before coding
- Model tiering: `plan-gatekeeper` downgraded to sonnet (fixed criteria, mechanically verifiable — trading process constraints for model cost)

Design inspired by Oh-My-OpenAgent's planning triple-chain (Metis boundary scanning / Momus triple verification). No source code from that project was used.

## License

MIT License
