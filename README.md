# Agent Skills Plugins

A curated collection of Claude Code skills and agents by Eric Grill.

## Installation

Add this marketplace:
```
/plugin marketplace add EricGrill/agents-skills-plugins
```

## Available Plugins

### nano-banana

Image generation MCP server using Google's Gemini API.

```
/plugin install nano-banana@agents-skills-plugins
```

**Tools:**
- `generate_image` - Generate a single image from a text prompt
- `generate_blog_images` - Generate a complete set of images for a blog post

**Requires:** `GEMINI_API_KEY` environment variable

### superpowers

Core skills library for Claude Code: TDD, debugging, collaboration patterns, and proven techniques.

```
/plugin install superpowers@agents-skills-plugins
```

**Skills (14):** brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills

**Commands:** `/brainstorm`, `/write-plan`, `/execute-plan`

**Attribution:** Forked from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent (MIT License)

### agent-orchestration

Context management and multi-agent orchestration with performance optimization tools.

```
/plugin install agent-orchestration@agents-skills-plugins
```

**Agents:** context-manager (elite AI context engineering specialist for dynamic context management, vector databases, knowledge graphs, and intelligent memory systems)

**Commands:** `/improve-agent` (agent performance optimization), `/multi-agent-optimize` (multi-agent performance engineering)

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### blockchain-web3

Blockchain development with Solidity security, DeFi protocols, NFT standards, and Web3 testing.

```
/plugin install blockchain-web3@agents-skills-plugins
```

**Agents:** blockchain-developer

**Skills (4):** defi-protocol-templates, nft-standards, solidity-security, web3-testing

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### business-analytics

Business analysis with data storytelling and KPI dashboard design.

```
/plugin install business-analytics@agents-skills-plugins
```

**Agents:** business-analyst

**Skills (2):** data-storytelling, kpi-dashboard-design

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### code-documentation

Code documentation with automated doc generation, code explanation, and tutorial engineering.

```
/plugin install code-documentation@agents-skills-plugins
```

**Agents:** code-reviewer, docs-architect, tutorial-engineer

**Commands:** `/code-explain`, `/doc-generate`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### comprehensive-review

Comprehensive code review with architecture, security, and PR enhancement.

```
/plugin install comprehensive-review@agents-skills-plugins
```

**Agents:** architect-review, code-reviewer, security-auditor

**Commands:** `/full-review`, `/pr-enhance`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### seo-analysis-monitoring

SEO analysis with authority building, cannibalization detection, and content refresh.

```
/plugin install seo-analysis-monitoring@agents-skills-plugins
```

**Agents:** seo-authority-builder, seo-cannibalization-detector, seo-content-refresher

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### seo-content-creation

SEO content creation with auditing, planning, and optimized writing.

```
/plugin install seo-content-creation@agents-skills-plugins
```

**Agents:** seo-content-auditor, seo-content-planner, seo-content-writer

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### seo-technical-optimization

Technical SEO with keyword strategy, meta optimization, snippets, and site structure.

```
/plugin install seo-technical-optimization@agents-skills-plugins
```

**Agents:** seo-keyword-strategist, seo-meta-optimizer, seo-snippet-hunter, seo-structure-architect

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### team-collaboration

Team collaboration with DX optimization, issue tracking, and standup notes.

```
/plugin install team-collaboration@agents-skills-plugins
```

**Agents:** dx-optimizer

**Commands:** `/issue`, `/standup-notes`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### unit-testing

Unit testing with debugging and test automation.

```
/plugin install unit-testing@agents-skills-plugins
```

**Agents:** debugger, test-automator

**Commands:** `/test-generate`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### python-development

Python development with Django, FastAPI, async patterns, and uv package management.

```
/plugin install python-development@agents-skills-plugins
```

**Agents:** django-pro, fastapi-pro, python-pro

**Skills (5):** async-python-patterns, python-packaging, python-performance-optimization, python-testing-patterns, uv-package-manager

**Commands:** `/python-scaffold`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### llm-application-dev

LLM application development with RAG, embeddings, LangChain, and prompt engineering.

```
/plugin install llm-application-dev@agents-skills-plugins
```

**Agents:** ai-engineer, prompt-engineer, vector-database-engineer

**Skills (8):** embedding-strategies, hybrid-search-implementation, langchain-architecture, llm-evaluation, prompt-engineering-patterns, rag-implementation, similarity-search-patterns, vector-index-tuning

**Commands:** `/ai-assistant`, `/langchain-agent`, `/prompt-optimize`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### javascript-typescript

JavaScript and TypeScript development with modern patterns and Node.js backend.

```
/plugin install javascript-typescript@agents-skills-plugins
```

**Agents:** javascript-pro, typescript-pro

**Skills (4):** javascript-testing-patterns, modern-javascript-patterns, nodejs-backend-patterns, typescript-advanced-types

**Commands:** `/typescript-scaffold`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### git-pr-workflows

Git and PR workflows with code review, onboarding, and PR enhancement.

```
/plugin install git-pr-workflows@agents-skills-plugins
```

**Agents:** code-reviewer

**Commands:** `/git-workflow`, `/onboard`, `/pr-enhance`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### game-development

Game development with Unity, Godot, and Minecraft Bukkit plugin development.

```
/plugin install game-development@agents-skills-plugins
```

**Agents:** minecraft-bukkit-pro, unity-developer

**Skills (2):** godot-gdscript-patterns, unity-ecs-patterns

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### full-stack-orchestration

Full-stack orchestration with deployment, performance, security, and test automation.

```
/plugin install full-stack-orchestration@agents-skills-plugins
```

**Agents:** deployment-engineer, performance-engineer, security-auditor, test-automator

**Commands:** `/full-stack-feature`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### content-marketing

Content marketing with content strategy and search specialist agents.

```
/plugin install content-marketing@agents-skills-plugins
```

**Agents:** content-marketer, search-specialist

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### context-management

Context management with save and restore capabilities.

```
/plugin install context-management@agents-skills-plugins
```

**Agents:** context-manager

**Commands:** `/context-restore`, `/context-save`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### customer-sales-automation

Customer support and sales automation agents.

```
/plugin install customer-sales-automation@agents-skills-plugins
```

**Agents:** customer-support, sales-automator

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### database-design

Database architecture and SQL optimization with PostgreSQL expertise.

```
/plugin install database-design@agents-skills-plugins
```

**Agents:** database-architect, sql-pro

**Skills (1):** postgresql

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### data-validation-suite

Data validation and backend security coding.

```
/plugin install data-validation-suite@agents-skills-plugins
```

**Agents:** backend-security-coder

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### deployment-strategies

Deployment engineering with Terraform and infrastructure as code.

```
/plugin install deployment-strategies@agents-skills-plugins
```

**Agents:** deployment-engineer, terraform-specialist

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### developer-essentials

Essential developer skills for monorepos, debugging, testing, and build optimization.

```
/plugin install developer-essentials@agents-skills-plugins
```

**Agents:** monorepo-architect

**Skills (11):** auth-implementation-patterns, bazel-build-optimization, code-review-excellence, debugging-strategies, e2e-testing-patterns, error-handling-patterns, git-advanced-workflows, monorepo-management, nx-workspace-patterns, sql-optimization-patterns, turborepo-caching

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### documentation-generation

Documentation generation with API docs, architecture diagrams, and tutorials.

```
/plugin install documentation-generation@agents-skills-plugins
```

**Agents:** api-documenter, docs-architect, mermaid-expert, reference-builder, tutorial-engineer

**Skills (3):** architecture-decision-records, changelog-automation, openapi-spec-generation

**Commands:** `/doc-generate`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### frontend-mobile-development

Frontend and mobile development with React, Next.js, React Native, and Tailwind.

```
/plugin install frontend-mobile-development@agents-skills-plugins
```

**Agents:** frontend-developer, mobile-developer

**Skills (4):** nextjs-app-router-patterns, react-native-architecture, react-state-management, tailwind-design-system

**Commands:** `/component-scaffold`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

### frontend-mobile-security

Frontend and mobile security with XSS scanning and secure coding practices.

```
/plugin install frontend-mobile-security@agents-skills-plugins
```

**Agents:** frontend-developer, frontend-security-coder, mobile-security-coder

**Commands:** `/xss-scan`

**Attribution:** From [wshobson/agents](https://github.com/wshobson/agents) (MIT License)

## License

MIT
