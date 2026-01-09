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

---

## Stats

| Metric | Count |
|--------|-------|
| Total Plugins | 28 |
| Total Agents | 60+ |
| Total Skills | 70+ |
| Total Commands | 30+ |

---

## Attribution

Plugins in this marketplace come from:

- **[obra/superpowers](https://github.com/obra/superpowers)** by Jesse Vincent - Core skills library
- **[wshobson/agents](https://github.com/wshobson/agents)** - Specialized agents and skills
- **Original** - nano-banana, plugin-finder

All plugins are MIT licensed.

---

## Contributing

Want to add a plugin to the marketplace? Open an issue or PR!

The marketplace auto-syncs weekly from upstream sources to stay current.

---

## License

MIT
