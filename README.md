<p align="center">
  <h1 align="center">Agent Skills Plugins</h1>
  <p align="center">
    <strong>A curated marketplace of Claude Code plugins, agents, and skills</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> |
    <a href="#-plugin-catalog">Catalog</a> |
    <a href="#-all-plugins">Full List</a> |
    <a href="#-contributing">Contributing</a>
  </p>
</p>

---

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add EricGrill/agents-skills-plugins

# Install any plugin
/plugin install <plugin-name>@agents-skills-plugins
```

**New to Claude Code plugins?** Start with **superpowers** - it includes essential skills for TDD, debugging, and code review that work with any project.

---

## Plugin Catalog

### By Category

| Category | Plugins | Best For |
|----------|---------|----------|
| [Core & Workflows](#-core--workflows) | superpowers, developer-essentials, git-pr-workflows | Every developer |
| [Documents & Productivity](#-documents--productivity) | awesome-claude-skills (27 skills!) | Office docs, media, productivity |
| [Languages](#-languages) | python-development, javascript-typescript | Language-specific development |
| [AI & LLM](#-ai--llm-development) | llm-application-dev, agent-orchestration | Building AI applications |
| [Code Quality](#-code-quality) | comprehensive-review, unit-testing, code-documentation | Better code |
| [Frontend & Mobile](#-frontend--mobile) | frontend-mobile-development, frontend-mobile-security | Web & mobile apps |
| [DevOps](#-devops--infrastructure) | deployment-strategies, full-stack-orchestration | Infrastructure & deployment |
| [SEO & Marketing](#-seo--marketing) | seo-content-creation, content-marketing | Content & SEO |
| [Data & Backend](#-data--backend) | database-design, data-validation-suite | Data management |
| [Specialized](#-specialized) | blockchain-web3, game-development | Domain-specific |

---

## All Plugins

### Core & Workflows

Essential plugins that every developer should consider.

<details>
<summary><b>superpowers</b> - Core skills library (14 skills, 3 commands)</summary>

The foundation for effective Claude Code usage. Includes TDD, debugging, code review, and collaboration patterns.

```
/plugin install superpowers@agents-skills-plugins
```

| Skills | Commands |
|--------|----------|
| brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills | `/brainstorm` `/write-plan` `/execute-plan` |

*Forked from [obra/superpowers](https://github.com/obra/superpowers)*

</details>

<details>
<summary><b>developer-essentials</b> - Monorepos, debugging, testing (11 skills)</summary>

Essential patterns for modern development workflows including monorepo management, build optimization, and advanced git.

```
/plugin install developer-essentials@agents-skills-plugins
```

| Agents | Skills |
|--------|--------|
| monorepo-architect | auth-implementation-patterns, bazel-build-optimization, code-review-excellence, debugging-strategies, e2e-testing-patterns, error-handling-patterns, git-advanced-workflows, monorepo-management, nx-workspace-patterns, sql-optimization-patterns, turborepo-caching |

</details>

<details>
<summary><b>git-pr-workflows</b> - Git and PR automation (3 commands)</summary>

Streamline your git workflow with code review, onboarding, and PR enhancement tools.

```
/plugin install git-pr-workflows@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| code-reviewer | `/git-workflow` `/onboard` `/pr-enhance` |

</details>

<details>
<summary><b>team-collaboration</b> - DX optimization and standups (2 commands)</summary>

Improve team workflows with issue tracking and standup automation.

```
/plugin install team-collaboration@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| dx-optimizer | `/issue` `/standup-notes` |

</details>

<details>
<summary><b>context-management</b> - Save and restore context (2 commands)</summary>

Never lose your place. Save and restore conversation context across sessions.

```
/plugin install context-management@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| context-manager | `/context-save` `/context-restore` |

</details>

---

### Documents & Productivity

Work with Office documents, create media, and boost productivity.

<details>
<summary><b>awesome-claude-skills</b> - 27 practical skills from ComposioHQ</summary>

A comprehensive collection covering documents, creative media, development tools, business, and productivity.

```
/plugin install awesome-claude-skills@agents-skills-plugins
```

**Document Skills:**
| Skill | Description |
|-------|-------------|
| docx | Create, edit, analyze Word docs with tracked changes |
| pdf | Extract text, tables, metadata, merge & annotate PDFs |
| pptx | Read, generate, and adjust slides and layouts |
| xlsx | Spreadsheet manipulation: formulas, charts, data |

**Creative & Media:**
| Skill | Description |
|-------|-------------|
| canvas-design | Creates visual art in PNG and PDF |
| image-enhancer | Improves resolution, sharpness, clarity |
| slack-gif-creator | Animated GIFs optimized for Slack |
| theme-factory | Professional font and color themes |
| video-downloader | Download videos from YouTube |

**Development:**
| Skill | Description |
|-------|-------------|
| artifacts-builder | Multi-component HTML with React & Tailwind |
| changelog-generator | Git commits to release notes |
| mcp-builder | Create MCP servers for LLM integrations |
| skill-creator | Guide to building Claude Skills |
| webapp-testing | Test apps with Playwright |

**Business & Marketing:**
| Skill | Description |
|-------|-------------|
| brand-guidelines | Apply brand standards to artifacts |
| competitive-ads-extractor | Analyze competitor ads |
| domain-name-brainstormer | Generate and check domain names |
| internal-comms | Newsletters, FAQs, status reports |
| lead-research-assistant | Identify and qualify leads |

**Productivity:**
| Skill | Description |
|-------|-------------|
| file-organizer | Organize files, find duplicates |
| invoice-organizer | Automate invoice organization |
| content-research-writer | Research and refine content |
| meeting-insights-analyzer | Analyze meeting transcripts |
| raffle-winner-picker | Secure random selection |

*From [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)*

</details>

---

### Languages

Language-specific development tools and patterns.

<details>
<summary><b>python-development</b> - Django, FastAPI, async Python (5 skills)</summary>

Complete Python development toolkit with framework support and modern tooling.

```
/plugin install python-development@agents-skills-plugins
```

| Agents | Skills | Commands |
|--------|--------|----------|
| django-pro, fastapi-pro, python-pro | async-python-patterns, python-packaging, python-performance-optimization, python-testing-patterns, uv-package-manager | `/python-scaffold` |

</details>

<details>
<summary><b>javascript-typescript</b> - Modern JS/TS patterns (4 skills)</summary>

TypeScript and JavaScript development with modern patterns and Node.js backend support.

```
/plugin install javascript-typescript@agents-skills-plugins
```

| Agents | Skills | Commands |
|--------|--------|----------|
| javascript-pro, typescript-pro | javascript-testing-patterns, modern-javascript-patterns, nodejs-backend-patterns, typescript-advanced-types | `/typescript-scaffold` |

</details>

---

### AI & LLM Development

Build intelligent applications with RAG, embeddings, and prompt engineering.

<details>
<summary><b>llm-application-dev</b> - RAG, embeddings, LangChain (8 skills)</summary>

Everything you need to build production LLM applications.

```
/plugin install llm-application-dev@agents-skills-plugins
```

| Agents | Skills | Commands |
|--------|--------|----------|
| ai-engineer, prompt-engineer, vector-database-engineer | embedding-strategies, hybrid-search-implementation, langchain-architecture, llm-evaluation, prompt-engineering-patterns, rag-implementation, similarity-search-patterns, vector-index-tuning | `/ai-assistant` `/langchain-agent` `/prompt-optimize` |

</details>

<details>
<summary><b>agent-orchestration</b> - Multi-agent coordination (2 commands)</summary>

Orchestrate complex multi-agent workflows with context management and performance optimization.

```
/plugin install agent-orchestration@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| context-manager | `/improve-agent` `/multi-agent-optimize` |

</details>

<details>
<summary><b>multi-agent-patterns</b> - Architecture patterns for multi-agent systems</summary>

Design and implement multi-agent architectures with supervisor, swarm, and hierarchical patterns.

```
/plugin install multi-agent-patterns@agents-skills-plugins
```

**Patterns Covered:**
| Pattern | Description |
|---------|-------------|
| Supervisor/Orchestrator | Central control, delegating to specialists |
| Peer-to-Peer/Swarm | Direct agent communication, flexible handoffs |
| Hierarchical | Layered abstraction and coordination |

**Key Concepts:** Context isolation, token economics, parallelization strategies, consensus mechanisms, failure mode handling.

*From [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)*

</details>

<details>
<summary><b>ai-investigator</b> - Enterprise AI case study analyzer</summary>

Analyze enterprise AI case studies using Claude and Firecrawl APIs with automatic discovery and report generation.

```
/plugin install ai-investigator@agents-skills-plugins
```

**Reports Generated:**
| Report Type | Description |
|-------------|-------------|
| Individual | Executive summary, AI strategy, tech implementation, business impact |
| Cross-Case | Patterns, success factors, technology trends, ROI metrics |
| Executive Dashboard | Company profiles, tech stacks, success metrics |

**Modes:** CSV analysis (specific URLs) or Website discovery (automatic crawl)

*From [muratcankoylan/AI-Investigator](https://github.com/muratcankoylan/AI-Investigator)*

</details>

---

### Code Quality

Write better code with reviews, testing, and documentation.

<details>
<summary><b>comprehensive-review</b> - Architecture and security review (2 commands)</summary>

Deep code review covering architecture, security, and PR quality.

```
/plugin install comprehensive-review@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| architect-review, code-reviewer, security-auditor | `/full-review` `/pr-enhance` |

</details>

<details>
<summary><b>unit-testing</b> - Testing and debugging (1 command)</summary>

Automated test generation and systematic debugging.

```
/plugin install unit-testing@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| debugger, test-automator | `/test-generate` |

</details>

<details>
<summary><b>code-documentation</b> - Docs and tutorials (2 commands)</summary>

Generate documentation, explain code, and create tutorials.

```
/plugin install code-documentation@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| code-reviewer, docs-architect, tutorial-engineer | `/code-explain` `/doc-generate` |

</details>

<details>
<summary><b>documentation-generation</b> - API docs and diagrams (3 skills)</summary>

Professional documentation with API specs, Mermaid diagrams, and architecture records.

```
/plugin install documentation-generation@agents-skills-plugins
```

| Agents | Skills | Commands |
|--------|--------|----------|
| api-documenter, docs-architect, mermaid-expert, reference-builder, tutorial-engineer | architecture-decision-records, changelog-automation, openapi-spec-generation | `/doc-generate` |

</details>

---

### Frontend & Mobile

Build modern web and mobile applications.

<details>
<summary><b>frontend-mobile-development</b> - React, Next.js, React Native (4 skills)</summary>

Full-stack frontend development with modern frameworks and design systems.

```
/plugin install frontend-mobile-development@agents-skills-plugins
```

| Agents | Skills | Commands |
|--------|--------|----------|
| frontend-developer, mobile-developer | nextjs-app-router-patterns, react-native-architecture, react-state-management, tailwind-design-system | `/component-scaffold` |

</details>

<details>
<summary><b>frontend-mobile-security</b> - XSS scanning and secure coding (1 command)</summary>

Security-focused frontend development with vulnerability scanning.

```
/plugin install frontend-mobile-security@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| frontend-developer, frontend-security-coder, mobile-security-coder | `/xss-scan` |

</details>

<details>
<summary><b>ios-simulator-skill</b> - iOS testing automation (21 scripts)</summary>

Production-ready iOS simulator automation with semantic navigation using accessibility APIs.

```
/plugin install ios-simulator-skill@agents-skills-plugins
```

**Categories:**
| Category | Scripts |
|----------|---------|
| Build & Dev | build_and_test.py, log_monitor.py |
| Navigation | screen_mapper.py, navigator.py, gesture.py, keyboard.py, app_launcher.py |
| Testing | accessibility_audit.py, visual_diff.py, test_recorder.py, app_state_capture.py |
| Permissions | clipboard.py, status_bar.py, push_notification.py, privacy_manager.py |
| Lifecycle | simctl_boot.py, simctl_shutdown.py, simctl_create.py, simctl_delete.py, simctl_erase.py |

**Features:** Semantic navigation (find by meaning, not coordinates), 96% token reduction, WCAG compliance checking, CI/CD ready with JSON output.

*From [conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill)*

</details>

---

### DevOps & Infrastructure

Deploy, monitor, and manage infrastructure.

<details>
<summary><b>full-stack-orchestration</b> - End-to-end deployment (1 command)</summary>

Coordinate deployment, performance, security, and testing across your stack.

```
/plugin install full-stack-orchestration@agents-skills-plugins
```

| Agents | Commands |
|--------|----------|
| deployment-engineer, performance-engineer, security-auditor, test-automator | `/full-stack-feature` |

</details>

<details>
<summary><b>deployment-strategies</b> - Terraform and IaC</summary>

Infrastructure as code with Terraform expertise.

```
/plugin install deployment-strategies@agents-skills-plugins
```

| Agents |
|--------|
| deployment-engineer, terraform-specialist |

</details>

---

### SEO & Marketing

Optimize content for search and marketing.

<details>
<summary><b>seo-content-creation</b> - SEO writing and planning</summary>

Create SEO-optimized content with auditing, planning, and writing agents.

```
/plugin install seo-content-creation@agents-skills-plugins
```

| Agents |
|--------|
| seo-content-auditor, seo-content-planner, seo-content-writer |

</details>

<details>
<summary><b>seo-analysis-monitoring</b> - Authority and content health</summary>

Monitor SEO performance with authority building and content refresh detection.

```
/plugin install seo-analysis-monitoring@agents-skills-plugins
```

| Agents |
|--------|
| seo-authority-builder, seo-cannibalization-detector, seo-content-refresher |

</details>

<details>
<summary><b>seo-technical-optimization</b> - Keywords and meta tags</summary>

Technical SEO with keyword strategy, meta optimization, and site structure.

```
/plugin install seo-technical-optimization@agents-skills-plugins
```

| Agents |
|--------|
| seo-keyword-strategist, seo-meta-optimizer, seo-snippet-hunter, seo-structure-architect |

</details>

<details>
<summary><b>content-marketing</b> - Content strategy</summary>

Content marketing with strategy and search specialist agents.

```
/plugin install content-marketing@agents-skills-plugins
```

| Agents |
|--------|
| content-marketer, search-specialist |

</details>

<details>
<summary><b>ralph-wiggum-marketer</b> - Autonomous AI copywriter (4 commands)</summary>

Autonomous AI copywriter for SaaS content using the Ralph Wiggum pattern - iterative loops that ship content while you sleep.

```
/plugin install ralph-wiggum-marketer@agents-skills-plugins
```

| Commands | Description |
|----------|-------------|
| `/ralph-init` | Initialize a new content project |
| `/ralph-marketer` | Start the autonomous copywriter loop |
| `/ralph-status` | Check content pipeline and progress |
| `/ralph-cancel` | Cancel the active loop |

**The Ralph Loop:** Read PRD → Check Progress → Pick Task → Execute → Verify → Commit → Update → Repeat

*From [muratcankoylan/ralph-wiggum-marketer](https://github.com/muratcankoylan/ralph-wiggum-marketer)*

</details>

<details>
<summary><b>beautiful-prose</b> - Forceful writing without AI tics</summary>

A hard-edged writing style skill for clean, exact, muscular prose free of modern AI cadence.

```
/plugin install beautiful-prose@agents-skills-plugins
```

**Registers:**
| Register | Style |
|----------|-------|
| founding_fathers | Formal, spare, civic gravity |
| literary_modern | Vivid, lean imagery (default) |
| cold_steel | Severe compression, punchy |
| journalistic | Crisp, factual, narrative clarity |

**Controls:** `DENSITY: lean|standard|dense`, `HEAT: cool|warm|hot`, `LENGTH: micro|short|medium|long`

*From [SHADOWPR0/beautiful_prose](https://github.com/SHADOWPR0/beautiful_prose)*

</details>

---

### Data & Backend

Database design, validation, and backend services.

<details>
<summary><b>database-design</b> - SQL and PostgreSQL (1 skill)</summary>

Database architecture and query optimization.

```
/plugin install database-design@agents-skills-plugins
```

| Agents | Skills |
|--------|--------|
| database-architect, sql-pro | postgresql |

</details>

<details>
<summary><b>data-validation-suite</b> - Backend security</summary>

Data validation and secure backend coding practices.

```
/plugin install data-validation-suite@agents-skills-plugins
```

| Agents |
|--------|
| backend-security-coder |

</details>

<details>
<summary><b>customer-sales-automation</b> - Support and sales</summary>

Automate customer support and sales workflows.

```
/plugin install customer-sales-automation@agents-skills-plugins
```

| Agents |
|--------|
| customer-support, sales-automator |

</details>

<details>
<summary><b>business-analytics</b> - KPIs and dashboards (2 skills)</summary>

Business analysis with data storytelling and dashboard design.

```
/plugin install business-analytics@agents-skills-plugins
```

| Agents | Skills |
|--------|--------|
| business-analyst | data-storytelling, kpi-dashboard-design |

</details>

---

### Specialized

Domain-specific plugins for specialized development.

<details>
<summary><b>blockchain-web3</b> - Solidity, DeFi, NFTs (4 skills)</summary>

Web3 development with smart contract security and DeFi protocols.

```
/plugin install blockchain-web3@agents-skills-plugins
```

| Agents | Skills |
|--------|--------|
| blockchain-developer | defi-protocol-templates, nft-standards, solidity-security, web3-testing |

</details>

<details>
<summary><b>game-development</b> - Unity, Godot, Minecraft (2 skills)</summary>

Game development across multiple engines and platforms.

```
/plugin install game-development@agents-skills-plugins
```

| Agents | Skills |
|--------|--------|
| minecraft-bukkit-pro, unity-developer | godot-gdscript-patterns, unity-ecs-patterns |

</details>

<details>
<summary><b>nano-banana</b> - AI image generation (MCP)</summary>

Generate images using Google's Gemini API.

```
/plugin install nano-banana@agents-skills-plugins
```

| Tools | Requires |
|-------|----------|
| `generate_image`, `generate_blog_images` | `GEMINI_API_KEY` |

</details>

<details>
<summary><b>rosetta-prompt</b> - Multi-provider prompt optimization</summary>

Adapts prompts for different AI providers using multi-agent ReAct loops with LangChain.

```
/plugin install rosetta-prompt@agents-skills-plugins
```

**Architecture:** Orchestrator spawns parallel optimizer agents for OpenAI, Anthropic, Google, etc.

*From [muratcankoylan/The-Rosetta-Prompt](https://github.com/muratcankoylan/The-Rosetta-Prompt)*

</details>

<details>
<summary><b>readwren</b> - Literary DNA extraction</summary>

Multi-agent interview system that extracts your literary preferences and generates reading profiles.

```
/plugin install readwren@agents-skills-plugins
```

**Features:** 12-turn adaptive interview, taste anchors, style signature mapping, vocabulary analysis.

*From [muratcankoylan/readwren](https://github.com/muratcankoylan/readwren)*

</details>

<details>
<summary><b>food-tour-planner</b> - AI food tour planning</summary>

Multi-agent food tour planner using LangChain DeepAgents and Google Maps API.

```
/plugin install food-tour-planner@agents-skills-plugins
```

**Agents:** Restaurant Finder, Neighborhood Researcher, Dashboard Creator.

*From [muratcankoylan/Food-tour-planner-agent](https://github.com/muratcankoylan/Food-tour-planner-agent)*

</details>

<details>
<summary><b>actual-code</b> - 7-agent code assessment generator</summary>

Analyzes GitHub repos and generates personalized coding challenges using Google Gemini.

```
/plugin install actual-code@agents-skills-plugins
```

**Pipeline:** Scanner → Code/PR/Issue/Dependency Analyzers → Problem Creator → QA Validator

*From [muratcankoylan/actual_code](https://github.com/muratcankoylan/actual_code)*

</details>

<details>
<summary><b>book-training</b> - Author style transfer with LoRA</summary>

Complete pipeline for training LLMs to write in specific author styles using SFT.

```
/plugin install book-training@agents-skills-plugins
```

**Results:** 97% loss reduction, ~50-70% human score on AI detectors.

*From [muratcankoylan/book-training](https://github.com/muratcankoylan/book-training)*

</details>

<details>
<summary><b>linkedin-analyzer</b> - LinkedIn profile insights</summary>

Analyze LinkedIn profiles using Cohere Command R+ for professional insights.

```
/plugin install linkedin-analyzer@agents-skills-plugins
```

**Features:** Post analysis, engagement metrics, professional growth recommendations.

*From [muratcankoylan/linkedin-analyzer](https://github.com/muratcankoylan/linkedin-analyzer)*

</details>

<details>
<summary><b>feed2context</b> - Feed to research report</summary>

One-click transformation of LinkedIn/X posts into detailed research reports.

```
/plugin install feed2context@agents-skills-plugins
```

**Pipeline:** Extract post → Build query (Kimi-K2) → Search & reason (Groq Compound) → Report

*From [muratcankoylan/feed2context](https://github.com/muratcankoylan/feed2context)*

</details>

---

## Stats

| Metric | Count |
|--------|-------|
| Total Plugins | 41 |
| Total Agents | 70+ |
| Total Skills | 110+ |
| Total Commands | 40+ |

---

## Attribution

Plugins in this marketplace come from:

- **[obra/superpowers](https://github.com/obra/superpowers)** by Jesse Vincent - Core skills library
- **[wshobson/agents](https://github.com/wshobson/agents)** - Specialized agents and skills
- **[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)** - Document & productivity skills
- **[conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill)** - iOS testing automation
- **[muratcankoylan](https://github.com/muratcankoylan)** - 10 plugins including multi-agent patterns, rosetta-prompt, readwren, actual-code, book-training, and more
- **[SHADOWPR0/beautiful_prose](https://github.com/SHADOWPR0/beautiful_prose)** - Writing style skill
- **Original** - nano-banana, plugin-finder

All plugins are MIT licensed.

---

## Contributing

Want to add a plugin to the marketplace? Open an issue or PR!

The marketplace auto-syncs weekly from upstream sources to stay current.

---

## License

MIT
