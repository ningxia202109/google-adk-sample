# AWS Kiro IDE：功能介绍与 SDD 实践体验

> 📅 更新时间：2026-05  
> 👤 面向读者：开发者  
> 🔗 官网：[kiro.dev](https://kiro.dev)

---

## 目录

- [什么是 Kiro](#什么是-kiro)
- [核心功能](#核心功能)
  - [Specs — 三文件系统](#specs--三文件系统)
  - [Steering Files — 持久上下文](#steering-files--持久上下文)
  - [Agent Hooks — 自动化质量门](#agent-hooks--自动化质量门)
  - [Skills — 可复用知识包](#skills--可复用知识包)
  - [Powers — 动态工具加载](#powers--动态工具加载)
- [SDD 工作流实践](#sdd-工作流实践)
  - [新项目](#新项目)
  - [已有项目](#已有项目)
- [定价](#定价)
- [个人体验与建议](#个人体验与建议)
  - [在 google-adk-sample 项目上的实际体验](#在-google-adk-sample-项目上的实际体验)
  - [做得好的地方](#做得好的地方)
  - [需要注意的地方](#需要注意的地方)
- [开源状态与已知限制](#开源状态与已知限制)
- [参考资源](#参考资源)

---

## 什么是 Kiro

Kiro 是 AWS 于 2025 年推出的 AI 原生 IDE，基于 VS Code 开源内核，由 Amazon Bedrock 上的 Claude 模型驱动。

它的核心理念是 **Spec-Driven Development（规格驱动开发，SDD）**——开发者先定义清晰的规格（Spec），再由 AI Agent 基于规格生成和维护代码。这从根本上解决了"AI 写得快但方向不对、改起来一团糟"的问题。

简单来说：**你负责定义正确，AI 负责执行正确。**

---

## 核心功能

### Specs — 三文件系统

Specs 是 Kiro 最核心的设计，将每个功能的开发过程结构化为三个 Markdown 文件，存放在 `.kiro/specs/` 目录下：

| 文件 | 职责 | 关键问题 |
|------|------|----------|
| `requirements.md` | 做什么——用户故事 + 验收标准 | 这个功能对用户意味着什么？ |
| `design.md` | 怎么设计——架构、数据模型、接口 | 技术上如何实现？ |
| `tasks.md` | 怎么拆解——Agent 执行清单 | 具体要改哪些文件、做哪些事？ |

**工作流：**

```
输入需求描述
    ↓
Kiro 生成 requirements.md 草稿
    ↓
✋ 人工审查（最重要的介入点）
    ↓
Kiro 生成 design.md
    ↓
✋ 人工确认技术方案
    ↓
生成 tasks.md → Agent 逐步实现
    ↓
需求变更 → 先改 Spec，再改代码
```

`requirements.md` 使用 **EARS 格式**（Easy Approach to Requirements Syntax）来写用户故事，这是一种由劳斯莱斯工程师开发的结构化需求写法，能有效避免需求歧义。

**关键价值：** 需求变更有完整的历史记录，始终知道"为什么这样改"。

---

### Steering Files — 持久上下文

Steering 文件存放在 `.kiro/steering/` 目录下，建议提交到 Git 与团队共享。它在每次会话中自动加载，确保 AI 始终遵循项目约定，不用每次重新解释背景。

**实际案例（来自 google-adk-sample 项目，三个文件）：**

**`.kiro/steering/project-overview.md`** — 项目布局、启动命令、服务端口：

```markdown
# Project Overview

This is a **Google ADK (Agent Development Kit) sample project** demonstrating
how to build enterprise-grade AI agent applications.

## Repository Layout
google-adk-sample/
├── src/
│   ├── common/                          # Shared infrastructure (models, plugins, tools)
│   ├── agent_react_number_guesser/      # ReAct pattern demo
│   ├── agent_progressive_disclosure/    # Planner+Executor loop demo
│   ├── agent_pd_troubleshooting/        # PlanReActPlanner + AgentTool demo
│   └── agent_with_skills_register_user/ # Dynamic skills (Claude-style) demo
├── dummy_fastapi_service/               # Companion REST backend (port 6060)
└── docker-compose/                      # Local observability stack

## Service Endpoints
| Service        | Port | Purpose                            |
|----------------|------|------------------------------------|
| ADK Web UI     | 8000 | Interactive agent chat interface   |
| FastAPI backend| 6060 | REST API used by agents            |
| OTLP collector | 5000 | OpenTelemetry trace receiver       |

## Resolving Unknown Library Usage
If you are unsure how to use an imported library or an internal ADK class, **do not guess**.
Locate the library source in the virtual environment:
  - `.venv/lib/python3.12/site-packages/<package_name>/`
Read the relevant source files before writing or suggesting code.
This applies especially to google-adk internals (BasePlugin, BaseToolset,
InvocationContext, ReadonlyContext, ToolContext).
```

**`.kiro/steering/coding-conventions.md`** — 提示词结构、工具约定、测试策略（节选关键部分）：

```markdown
# Coding Conventions

## Agent Instruction (Prompt) Structure
Every agent `instruction` string **must** follow the 4-layer pattern:
# [0] META-LAYER     — Identity, scope rejection, prompt-injection defense
# [1] OBSERVABILITY  — Mandatory <thought_process> XML before every action
# [2] FSM LOGIC      — Explicit state machine: Trigger → State → Action → Transition
# [3] TOOL CONTRACTS — Pre/post-conditions for each tool, semantic-logic mapping

## Prompt Variable Syntax
| Syntax  | Use                                    | Source               |
|---------|----------------------------------------|----------------------|
| `{var?}`| Runtime injection from Python (null-safe) | External environment |
| `<var>` | LLM-internal chain-of-thought variables | Model inference only |
**Never** use bare `{}` for LLM-internal variables — causes Python string formatting errors.

## HTTP Clients
- Use `httpx.AsyncClient` for async tool functions
- Always call `response.raise_for_status()` and wrap in `try/except` returning an error string

## Testing Policy
- Unit tests are **mandatory** for all Python tool functions and plugin classes
- Tests for agent definitions (LlmAgent, App) are **not required**
```

**`.kiro/steering/agent-patterns.md`** — 四种 Agent 模式的选择树（节选）：

```markdown
# Agent Development Patterns

## Choosing a Pattern
Is the task a single iterative loop with one tool?
  └─ YES → Pattern 1: ReAct

Does the task require multiple sequential API calls with validation between steps?
  └─ YES → Pattern 2: Progressive Disclosure (LoopAgent)

Does the task require strategic planning with isolated, safe execution?
  └─ YES → Pattern 3: PlanReActPlanner + AgentTool

Does the agent need to handle many different task domains dynamically?
  └─ YES → Pattern 4: Dynamic Skills
```

`inclusion` 字段控制加载时机：`always`（始终）、`fileMatch`（按文件类型）、`manual`（手动）。这三个文件都使用 `always`，确保每次会话都完整加载。

**核心价值：** 把团队的隐性知识显式化，新成员和 AI 都能快速对齐。

---

### Agent Hooks — 自动化质量门

Hooks 是由文件事件触发的自动化 Agent 动作。它把质量检查嵌入开发流程本身，而不是等到 CI 才发现问题。

**常用场景：**

| 触发时机 | 用途 |
|----------|------|
| 文件保存时 | 自动检查是否违反架构约束 |
| 新文件创建 | 自动生成对应的测试文件 |
| Task 完成后 | 运行测试套件，失败则停止并报告 |
| 手动触发 | 生成 API 文档、执行代码审查 |

Hook 通过自然语言描述来创建，例如：

> "每次 Agent 修改文件后，运行 `pytest`。如果测试失败，停止并报告具体错误，不继续下一个 task。"

**核心价值：** 从"事后补救"变成"过程内置"，Agent 自己也无法跳过质量检查。

---

### Skills — 可复用知识包

Skills 是遵循 [agentskills.io](https://agentskills.io) 开放标准的可移植知识包，用于给 Agent 注入专项知识，在需要时按需激活。

**与 Steering 的区别：**

| | Steering | Skill |
|--|----------|-------|
| 加载方式 | 每次会话自动加载 | 按需激活 |
| 内容类型 | 项目约束和规范 | 特定工作流的操作步骤 |
| 作用范围 | 始终生效 | 任务相关时生效 |
| 典型示例 | 技术栈约束、禁止事项 | 代码审查流程、API 设计规范 |

**目录结构：**

```
.kiro/skills/
└── api-design/
    ├── SKILL.md        # 必须：指令主文件
    ├── references/     # 可选：深度参考文档
    └── scripts/        # 可选：可执行脚本
```

**激活方式：** 聊天框输入 `/api-design` 手动触发，或 Kiro 根据上下文自动识别。

**跨工具兼容：** 同一个 Skill 可以在 Kiro、Claude Code、Cursor、Gemini CLI 等 40+ 工具中使用，一次编写，到处可用。

---

### Powers — 动态工具加载

Powers 是 Kiro 的动态 MCP 工具加载机制。传统方式会一次性加载所有集成工具，大量占用上下文窗口。Powers 则按需激活：

- 提到 "payment" → Stripe Power 自动启用
- 切换到数据库工作 → Supabase Power 激活，Stripe 自动卸载

**已支持的生态合作伙伴：** Datadog、Figma、Neon、Netlify、Postman、Supabase、Stripe 等。

---

## SDD 工作流实践

### 新项目

```
第 1 步：建立 Steering 文件
         技术栈 + 架构约定 + 禁止事项
              ↓
第 2 步：创建第一个 Spec
         需求描述 → requirements.md → 人工确认
              ↓
第 3 步：确认 design.md
         重点检查：方案是否符合架构约定？有没有引入不必要的依赖？
              ↓
第 4 步：执行 tasks.md
         Agent 逐 task 实现，开启 Supervised 模式逐文件审查
              ↓
第 5 步：配置 Hooks
         保存时检查规范，完成后跑测试
```

**Supervised 模式：** 当 Agent 修改多个文件时，可以逐文件审查，有选择地接受或拒绝每项改动。建议在新项目初期开启，熟悉 Kiro 的行为习惯后再适当放开。

---

### 已有项目

对于已有代码库，Kiro 提供两种专门的 Spec 类型，避免走完整的三文件流程造成不必要的摩擦。

**Design-First Spec** — 有明确技术方案时

先写 `design.md`（你已经知道怎么做），再由 Kiro 反向推导 `requirements.md`。适合在现有架构内新增功能，不破坏已有约定。

**Bugfix Spec** — 外科手术式修复

结构化为三个部分：

```
Current Behavior（当前行为）：
  "当用户提交含特殊字符的表单时，系统崩溃报 500"

Expected Behavior（期望行为）：
  "应清洗输入并正常处理，返回 200"

Unchanged Behavior（不变行为）：← 最重要
  "合法表单的处理流程必须保持不变"
```

"不变行为"字段是关键——明确告诉 Agent 什么不能动，防止修 Bug 时引入新问题。

**Brownfield 冷启动建议：**
1. 先让 Kiro 分析代码库，生成项目概览文档
2. 将分析结果整理为 Steering 文件（一次性投资，值得花时间）
3. 从低风险的新功能开始试水，不要第一个就拿核心模块练手
4. 推行"改动必须带 Spec"的团队规范，逐步提升 Spec 覆盖率

---

## 定价

| 套餐 | 价格 | Agentic 交互次数 |
|------|------|-----------------|
| Free | 免费 | 50 次/月 |
| Pro | $19/月 | 1,000 次/月 |
| Pro+ | $39/月 | 3,000 次/月 |
| 超出部分 | $0.04/次 | 按需计费 |

> 💡 一次"Agentic 交互"可能是一个运行 3-5 分钟、跨多个文件的复杂任务，不等同于一条聊天消息。免费版的 50 次对于试用评估已经足够。

---

## 个人体验与建议

> **总体结论：不推荐在生产团队中采用 Kiro。**  
> 核心原因有两点：第一，Kiro 是闭源软件，你无法审计也无法修改它的行为；第二，最关键的限制——生成 requirements.md、design.md、tasks.md 的内部 prompt 逻辑完全封闭，不能替换 LLM，也不能修改 Spec 生成的配置。这意味着你把最核心的工程决策（需求怎么拆、方案怎么设计、任务怎么组织）托付给了一个黑盒，而这个黑盒既不透明也不可定制。SDD 的价值在于让流程可控，但 Kiro 的闭源设计恰恰让这个关键环节失控。

### 在 google-adk-sample 项目上的实际体验

本节记录了在一个真实的 Google ADK 多 Agent 项目（[google-adk-sample](https://github.com/ningxia202109/google-adk-sample)）上使用 Kiro 的具体经过，分两个阶段：建立 Steering 文件（[PR #14](https://github.com/ningxia202109/google-adk-sample/pull/14)）和为 ADK v2 升级创建完整 Spec（[PR #15](https://github.com/ningxia202109/google-adk-sample/pull/15)）。

#### 阶段一：为已有项目建立 Steering 文件

项目已有四种 Agent 模式（ReAct、Progressive Disclosure、PlanReActPlanner+AgentTool、Dynamic Skills）和一套共享基础设施（插件、工具集、模型配置）。直接对 Kiro 说"帮我改代码"，它根本不知道这些约定从哪来，也不知道哪些文件是禁区。

建立了三个 Steering 文件：

| 文件 | 内容 |
|------|------|
| `.kiro/steering/project-overview.md` | 项目布局、启动命令、服务端口、环境变量 |
| `.kiro/steering/coding-conventions.md` | 4 层指令结构、变量语法约定、插件用法、测试策略 |
| `.kiro/steering/agent-patterns.md` | 四种 Agent 模式的选择判断树和结构示例 |

**一个意外惊喜：Kiro 主动读取了 `.venv` 目录。** 在填写 `project-overview.md` 时，我提到项目依赖 `google-adk` 但说不清某些内部类的接口。Kiro 自动在 `.venv/lib/python3.12/site-packages/google/adk/` 里查找源码，读取 `BasePlugin`、`BaseToolset`、`InvocationContext` 的类定义，然后用实际接口填写了 Steering 文件——而不是凭空推断。这让 Steering 文件从一开始就是准确的。

这一步骤之后，所有后续对话都不需要再解释"为什么这里用 `httpx.AsyncClient`"或"instruction 为什么要分四层"——Steering 文件把这些都承载了。

**投入产出比：** 三个文件加在一起大约 370 行，花了半天。但这个投入把之前散落在口耳相传和代码注释里的隐性约定全都显式化了。

#### 阶段二：用 Spec 驱动 ADK v2 升级

ADK 1.x → 2.0 是一次有 Breaking Change 的大版本升级。用 Kiro 创建了一个完整的 Spec，存放在 `.kiro/specs/google-adk-v2-upgrade/`（[requirements.md](https://github.com/ningxia202109/google-adk-sample/blob/main/.kiro/specs/google-adk-v2-upgrade/requirements.md)、[design.md](https://github.com/ningxia202109/google-adk-sample/blob/main/.kiro/specs/google-adk-v2-upgrade/design.md)、[tasks.md](https://github.com/ningxia202109/google-adk-sample/blob/main/.kiro/specs/google-adk-v2-upgrade/tasks.md)）。

**requirements.md 的价值：** Kiro 生成的 requirements 文档包含了一个完整的 Breaking Change 分析矩阵（BC-1 到 BC-7），逐条判断每个变化对本项目的影响程度。这件事如果手工做，需要仔细对照官方迁移文档和项目代码。Kiro 在生成需求时已经把这个分析做了，而且有理有据：

```markdown
### BC-4: Broad `except Exception:` blocks in tools mask automatic retry
**Impact on this project**: Moderate.
所有 tool 函数用 except Exception as e: return f"Error: {str(e)}"。
这会阻止 ADK 2.0 的自动重试触发。项目需要决定是否采用重试行为。
```

这类分析很难靠"让 AI 直接改代码"得到——因为 AI 需要先理解现有代码结构，再对照升级文档，才能判断哪里有影响、影响有多大。Spec 流程强迫这个分析在动手之前完成。

**design.md 的关键决策：** 在技术方案阶段，Kiro 提出了一个重要的架构决策——对 BC-4（exception 处理影响自动重试）的回应：

> 设计决策：项目将保留当前 `except Exception as e: return f"Error: {str(e)}"` 模式。这是对 ADK 2.0 自动重试机制的有意退出。理由是：工具返回结构化错误字符串让 LLM 能够理解并恢复，比静默重试更可预测。不添加 `RetryConfig`。

这个决策如果不记录下来，下次有人改代码时可能会"顺手"改掉，引入难以发现的行为变化。

**tasks.md 的可操作性：** 生成的任务清单精确到具体操作：

```markdown
- [ ] 2.1 Verify all 11 ADK import paths resolve without `ImportError`
    - Attempt: from google.adk.apps.app import App
    - Attempt: from google.adk.agents import LlmAgent, LoopAgent
    - ...（逐条列出 11 个导入路径）
    - If any raises ImportError, update the affected source file(s) before proceeding
```

不是"检查导入是否正确"这种模糊说法，而是列出了需要验证的全部 11 个导入路径，并指定了如果失败该怎么处理。Agent 拿到这个清单可以逐条执行，不需要再做判断。

#### 整体感受

**Spec 的最大价值不是生成代码，而是强制把隐性判断变成显性文档。** Breaking Change 分析、架构决策、边界条件——这些通常藏在开发者脑子里，Spec 流程把它们逼出来写成文字。

**Steering 文件是"一次性投资，长期收益"。** 初始建立有成本，但之后每次对话都省去了重新交代背景的时间，而且 AI 的输出质量明显更稳定。

**Kiro 主动利用项目工具链这件事值得关注。** 主动读 `.venv` 查源码，这不是用户显式要求的——是 Kiro 根据上下文判断"我需要看实际接口才能给出准确答案"然后自己去找的。这种行为在处理框架内部 API 时特别有价值。

---

### 做得好的地方

**Bugfix Spec 的"不变行为"字段是亮点。** 在已有项目上修 Bug 最怕改坏其他功能，这个字段强迫你在动手前想清楚边界，Agent 也会严格遵守。

**Steering 文件解决了一个真实痛点。** 以前每次新开会话都要重新交代项目背景，有了 Steering，AI 每次启动都有完整的"项目手册"可以参考。

**Hooks 把质量检查变成了流程的一部分。** 不再依赖开发者自觉，Agent 完成 task 后自动跑测试，失败了自己也没法继续。

**Skills 的跨工具兼容性很实用。** 写一次，在 Kiro、Claude Code、Cursor 里都能用，团队知识不绑定在某个工具上。

### 需要注意的地方

**模型选择有限，不支持私有 LLM。** Kiro 提供多个 Claude 版本（Sonnet、Opus）和少量实验性开源模型，并有一个自动路由的 Auto 模式。但如果你的团队需要接入自己私有部署的模型、使用自己的 API Key，或者要求数据不出境——目前做不到。这是 Kiro 社区反映最多的限制之一，官方尚无明确的支持计划。

**Spec 生成逻辑是闭源的，无法直接修改。** Kiro 如何生成 requirements.md、design.md、tasks.md 的内部 prompt 逻辑你看不到，也改不了。你能做的是通过 Steering 文件间接影响输出风格和内容要求，但这是"引导"而非"控制"。如果你的团队需要完全掌控生成逻辑，Kiro 不是合适的选择。

**可以通过 Steering 间接定制 Spec 生成行为：** 创建 `.kiro/steering/specs.md`，在里面描述你对 requirements、design、tasks 的格式和内容要求，Kiro 会在生成时参考这些指令。这是目前唯一的定制途径。

**简单任务走完整 Spec 流程会增加摩擦。** 对于单文件的小修改，直接用 Vibe Chat 更合适，不必每次都走三文件流程。Kiro 自己也提供了 Vibe Chat 和 Spec Chat 两种模式，按需切换即可。

**Brownfield 冷启动需要投入。** 建立 Steering 文件不是一蹴而就的，需要对项目有足够的了解。但这个投入是值得的，而且顺便能梳理清楚很多之前说不清楚的隐性约定。

### 建议的引入节奏

```
第 1-2 天：用免费版跑一个完整的新功能 Spec 流程，感受节奏
第 3-5 天：建立项目的 Steering 文件，补充团队规范
第 1-2 周：在团队内推行"改动带 Spec"的规范
长期：把 Steering 和 Skills 作为团队知识库持续维护
```

### 适合谁

✅ 需要多人协作、规格需要对齐的团队  
✅ 生产级项目，对可追溯性有要求  
✅ 在 AWS 生态上构建系统  
✅ 希望把 AI 编程从"快速试验"升级为"可靠工程"  

❌ 纯粹的个人快速原型（Cursor 体验更流畅）  
❌ 需要接入私有/自托管 LLM 的团队  
❌ 需要完全掌控 Spec 生成逻辑的场景  
❌ 数据合规要求不能使用外部 AI 服务的企业  

---

## 开源状态与已知限制

### Kiro 是开源软件吗？

**不是。** Kiro IDE 和 Kiro CLI 均以"AWS Content"形式授权，受 AWS Customer Agreement 约束，版权归 Amazon.com 所有。虽然底层基于 VS Code 的开源内核（Code OSS）构建，但 Kiro 本身是闭源的 AWS 专有软件。

### 模型选择

Kiro 目前支持以下模型，可在模型选择器中切换：

- **Auto**：自动路由器，结合多个前沿模型按任务复杂度优化质量/成本比
- **Claude Opus 4.7**（Pro/Pro+ 用户）：最强能力，带自适应思考
- **Claude Sonnet 4.6**：主力编码模型，1M 上下文窗口
- **实验性开源模型**：少量开源权重模型，实验性支持

不同模型有不同的 credit 消耗倍率（0.05x ～ 1.3x）。

**不支持的场景：**
- ❌ 使用自己的 API Key（Bedrock 或 Anthropic）
- ❌ 接入私有/自托管模型
- ❌ 数据不出境要求

这些是 Kiro 社区 GitHub Issues 里反映最多的限制，官方目前没有明确的支持计划。

### Spec 生成逻辑的可定制性

Kiro 内部如何生成 requirements.md、design.md、tasks.md 的 prompt 逻辑是闭源的。

| 能力 | 是否支持 |
|------|---------|
| 查看 Spec 生成的内部 prompt | ❌ |
| 通过 Steering 文件影响生成风格 | ✅ |
| 直接编辑生成后的 Spec 文件 | ✅ |
| 导入已有需求文档生成 Spec | ✅ |
| 完全替换生成逻辑 | ❌ |

**Steering 是唯一的定制入口：** 在 `.kiro/steering/specs.md` 中描述你对 Spec 格式、内容、顺序的要求，Kiro 会在生成时参考。这是"引导"而非"控制"，效果取决于描述的清晰程度。

### 如果你需要完全控制

考虑以下替代方案：

- **Claude Code + CLAUDE.md**：完全透明，模型可换，Spec 生成 prompt 完全由你写
- **GitHub spec-kit**：所有 artifacts 都在你的 workspace 里，通过 slash command 交互，开源可审计
- **自建 SDD 流程**：用任意 AI 工具 + 自己的 Spec 模板，没有任何黑盒

---



- [Kiro 官方文档](https://kiro.dev/docs/)
- [Kiro Blog — Specs, Bugfix and Design-First](https://kiro.dev/blog/specs-bugfix-and-design-first/)
- [agentskills.io — Agent Skills 开放标准](https://agentskills.io)
- [awesome-agent-skills — Skill 资源导航](https://github.com/skillmatic-ai/awesome-agent-skills)
- [Anthropic 官方 Skills 仓库](https://github.com/anthropics/skills)

---

*文档基于 Kiro 2025-2026 版本整理。如内容有变化欢迎提 PR 或直接修改。*
