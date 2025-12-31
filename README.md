# Google ADK Sample

Leveraging the Google Agent Development Kit (ADK) to build robust, enterprise-grade, and production-ready AI agent applications.

## Index

- [Agents](#agents)
  - [NumberGuesser Agent](#numberguesser-agent)
  - [Progressive Disclosure Agent](#progressive-disclosure-agent)
  - [PD Troubleshooting Agent](#pd-troubleshooting-agent)
- [Services](#services)
  - [Dummy FastAPI Service](#dummy-fastapi-service)
- [Setup](#setup)
  - [Environment Configuration](#environment-configuration)
  - [Installation and Running](#installation-and-running)
- [Dependencies](#dependencies)

## Agents

### NumberGuesser Agent

A proof-of-concept **ReAct (Reasoning + Acting)** agent that demonstrates the core principles of agentic AI:

- **Thinking**: Agent analyzes the current state and plans actions
- **Acting**: Agent calls tools to interact with the environment
- **Observing**: Agent receives feedback from tool outputs
- **Rethinking**: Agent adjusts strategy based on observations
- **Iteration**: Process repeats until task completion

The agent plays a number guessing game where it reasons about the target number, makes guesses using the `guess_number` tool, observes the feedback, and refines its strategy accordingly.

**Location**: `src/agent_react_number_guesser/`  
**Quick Start**: See [Agent README](src/agent_react_number_guesser/README.md) for detailed instructions.

### Progressive Disclosure Agent

A multi-agent system that demonstrates the **Progressive Disclosure** pattern for solving complex, multi-step tasks:

- **Decomposition**: Breaks complex tasks into smaller, manageable sub-tasks
- **Context Management**: Discloses only relevant information (e.g., specific API docs) for each step to optimize LLM performance
- **Iterative Execution**: Uses a `LoopAgent` to coordinate a **Planner** and an **Executor** until the goal is achieved
- **Verification**: Validates results at each step before proceeding

This agent interacts with an external API service to perform multi-step operations like finding a user and adding them to a team, ensuring each step is correctly executed and verified.

**Location**: `src/agent_progressive_disclosure/`  
**Quick Start**: See [Agent README](src/agent_progressive_disclosure/README.md) for detailed instructions.

### PD Troubleshooting Agent

A sophisticated multi-agent system that automates system diagnostics using advanced **Google ADK** features and the **Progressive Disclosure** pattern:

-   **ReAct Planner**: Uses a `PlanReActPlanner` to intelligently decompose user symptoms, retrieve relevant context, and adapt plans based on executor feedback.
-   **Progressive Disclosure**: Only discloses the most relevant troubleshooting guides and API documentation to the executor, reducing noise and increasing precision.
-   **Execution Isolation**: Leverages `AgentTool` to encapsulate detailed API interactions within a specialized executor agent, abstracting high-level results back to the planner.
-   **Context Optimization**: Uses `include_contents="none"` and `temperature=0.0` for deterministic, stateless execution focused entirely on the current troubleshooting guide.

This agent demonstrates how to build enterprise-grade troubleshooting workflows by separating strategic planning from isolated technical execution.

**Location**: `src/agent_pd_troubleshooting/`  
**Quick Start**: See [Agent README](src/agent_pd_troubleshooting/README.md) for detailed instructions.

## Services

### Dummy FastAPI Service

A companion backend service used by the agents to demonstrate real-world API interactions. It provides:

- **User Management**: Endpoints for listing and managing user profiles and their habits.
- **Team Management**: Endpoints for creating teams and managing team memberships with validation logic (e.g., habit matching).
- **Interactive Documentation**: Auto-generated API specs that agents can retrieve and analyze at runtime.

This service allows the agents to practice "reasoning over APIs" and performing multi-step operations in a controlled yet realistic environment.

**Location**: `dummy_fastapi_service/`

## Setup

### Environment Configuration

Set up your Google API key:

```bash
export GOOGLE_API_KEY=your_api_key_here
```

Or create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_api_key_here
```

### Installation and Running

```bash
uv sync
./start.sh
```

Then access the web interface at `http://127.0.0.1:8000`

## Dependencies

- google-adk
- litellm
