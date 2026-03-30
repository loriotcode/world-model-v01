# Claude Code — Plugins & Skills Audit

**Generated**: 2026-03-30
**Project**: world-model-v01
**Scope**: Available plugins and skills for this session

---

## 🎯 Official Anthropic Skills

### Code Quality & Debugging
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `anthropic-skills:focused-fix` | "fix X", "make Y work", "Z module broken" | Deep-dive systematic debugging of specific features |
| `anthropic-skills:simplify` | After code edits | Review code for reuse, quality, efficiency |
| `superpowers:systematic-debugging` | Any bug/test failure | Structured debugging before proposing fixes |

### Development Workflows
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `superpowers:writing-plans` | Multi-step tasks with specs | Design implementation strategy before coding |
| `superpowers:test-driven-development` | Any feature/bugfix | TDD workflow (tests first) |
| `superpowers:verification-before-completion` | Before claiming work done | Verify fixes/tests before merge |
| `superpowers:requesting-code-review` | After major features | Request structured code review |
| `superpowers:receiving-code-review` | After review feedback | Process feedback rigorously |

### Branching & Isolation
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `superpowers:using-git-worktrees` | Start feature work | Isolated git worktrees for safe development |
| `superpowers:finishing-a-development-branch` | After implementation complete | Options for merge/PR/cleanup |

### Advanced Orchestration
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `superpowers:brainstorming` | Before creative work (features, components) | Explore intent & design before implementation |
| `superpowers:executing-plans` | Execute written implementation plan | Run plan with review checkpoints |
| `superpowers:subagent-driven-development` | Multi-task execution in session | Independent parallel tasks |
| `superpowers:dispatching-parallel-agents` | 2+ independent tasks | Parallel agent coordination |

### Configuration & Setup
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `update-config` | Automate behaviors via settings.json | Configure hooks, env, harness behavior |
| `keybindings-help` | Customize keyboard shortcuts | Rebind keys, add chords |
| `anthropic-skills:skill-creator` | Create/edit/optimize skills | Skill development and testing |

### Productivity Tools
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `loop` | Recurring tasks/polling | Run prompt on interval (e.g. `/loop 5m /foo`) |
| `anthropic-skills:schedule` | Cron jobs, automated tasks | Schedule recurring remote agents |

---

## 📚 File & Document Skills

| Skill | Formats | Purpose |
|--------|---------|---------|
| `anthropic-skills:pdf` | `.pdf` | Read, extract, merge, split, watermark PDFs |
| `anthropic-skills:xlsx` | `.xlsx`, `.xlsm`, `.csv`, `.tsv` | Read, edit, compute formulas, format spreadsheets |
| `anthropic-skills:docx` | `.docx` | Create, read, edit Word documents |
| `anthropic-skills:pptx` | `.pptx` | Create, read, edit PowerPoint presentations |

---

## 🎮 Domain-Specific Skills

### Web Animation
| Skill | Purpose |
|-------|---------|
| `anthropic-skills:animejs-animation` | High-performance JS animations (complex tweens, timing) |

### Game Development
| Skill | Purpose |
|-------|---------|
| `anthropic-skills:2d-games` | 2D sprites, tilemaps, physics, camera |
| `2d-games` | Same as above (local variant) |

### Motion & Animation Performance
| Skill | Purpose |
|-------|---------|
| `fixing-motion-performance` | Audit/fix animation jank (layout thrashing, scroll-linked motion, blur) |

### AI & LLM Development
| Skill | Purpose |
|-------|---------|
| `anthropic-skills:python-patterns` | Python best practices, async, type hints, architecture |
| `claude-api` | Build with Claude API / Anthropic SDK (triggers: `anthropic` imports) |
| `senior-prompt-engineer` | Optimize prompts, design templates, eval outputs, agentic systems, RAG |
| `prompting-techniques` | Master guide for CLAUDE.md instructions |

### Research & Web
| Skill | Purpose |
|-------|---------|
| `anthropic-skills:websearch` | Quick web search for current information |

---

## 🔧 Project-Specific Skills

| Skill | Purpose |
|-------|---------|
| `focusing-fix` | Local variant of `focused-fix` |
| `prompting-techniques` | Local variant for CLAUDE.md optimization |
| `senior-prompt-engineer` | Local variant for prompt engineering |

---

## 🚫 Deprecated Skills (Do Not Use)

| Skill | Replacement |
|-------|-------------|
| `superpowers:brainstorm` | `superpowers:brainstorming` |
| `superpowers:execute-plan` | `superpowers:executing-plans` |
| `superpowers:write-plan` | `superpowers:writing-plans` |

---

## 📋 Quick Reference: When to Use Each

### Code Fixes & Debugging
- **Single bug fix** → Use Bash/Edit directly
- **Systematic debugging** → `superpowers:systematic-debugging`
- **Specific feature broken** → `anthropic-skills:focused-fix`
- **After coding** → `anthropic-skills:simplify`

### Features & Implementations
- **New feature planned** → `superpowers:brainstorming` → `superpowers:writing-plans`
- **Multi-step implementation** → `superpowers:subagent-driven-development`
- **Independent parallel tasks** → `superpowers:dispatching-parallel-agents`

### Quality Assurance
- **Before merge** → `superpowers:verification-before-completion`
- **Code review request** → `superpowers:requesting-code-review`
- **Review feedback received** → `superpowers:receiving-code-review`

### Optimization
- **Prompt engineering** → `senior-prompt-engineer`
- **Animation performance** → `fixing-motion-performance`
- **Code quality review** → `anthropic-skills:simplify`

---

## 🎯 wm-v0.1 Recommended Workflow

For **isometric engine development** (`feat/iso-engine`):

1. **Feature brainstorm** → `/skill superpowers:brainstorming`
2. **Plan implementation** → `/skill superpowers:writing-plans`
3. **Develop isolated** → `/skill superpowers:using-git-worktrees`
4. **Debug issues** → `/skill superpowers:systematic-debugging`
5. **Verify changes** → `/skill superpowers:verification-before-completion`
6. **Request review** → `/skill superpowers:requesting-code-review`
7. **Complete branch** → `/skill superpowers:finishing-a-development-branch`

---

**Last updated**: 2026-03-30
