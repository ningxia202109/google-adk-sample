# Agent Progressive Disclosure Troubleshooting

This project demonstrates a multi-agent troubleshooting system built using the **Google Agent Development Kit (ADK)**. It showcases how to use advanced planning and delegation to solve complex system issues in a safe and structured manner.

## Technical Stack & ADK Components

The project leverages several key components from the Google ADK:

### 1. `PlanReActPlanner`
The `agent_troubleshooting_planner` utilizes the `PlanReActPlanner`. This planner enables the agent to:
- **Plan**: Break down a high-level user request (e.g., "one user cannot join a team") into a sequence of logical steps.
- **Act & React**: Execute those steps using available tools and adapt the plan based on the feedback or results obtained at each step.

### 2. `AgentTool`
This component is used to implement a **Multi-Agent Orchestration** pattern. 
- The `agent_troubleshooter` is wrapped in an `AgentTool` and provided as a tool to the `agent_troubleshooting_planner`.
- This allows the planner agent to delegate the actual execution of troubleshooting steps (API calls) to a specialized worker agent.

### 3. `generate_content_config`
Both agents are configured using `GenerateContentConfig`.
- In this project, it is specifically used to set `temperature=0.0` for both agents.
- This ensures deterministic and consistent behavior, which is critical for system troubleshooting and planning.

### 4. `include_contents="none"`
The `agent_troubleshooter` is configured with `include_contents="none"`.
- This is an optimization for context management. 
- It tells the ADK not to automatically include the full conversation history in every request to the model, which is useful when the agent's task is focused on executing a specific, self-contained guide provided by the planner.

## Project Architecture

The system consists of two specialized agents:

1.  **Troubleshooting Planner (`agent_troubleshooting_planner`)**:
    - **Role**: Senior Expert Planner.
    - **Tools**: `search_issue_by_symptom` (Mock VectorDB), `retrieve_service_documentation` (API Specs), and the `agent_troubleshooter` (via `AgentTool`).
    - **Workflow**: Analyzes symptoms, retrieves documentation, creates a troubleshooting plan, and delegates execution.

2.  **Troubleshooter Executor (`agent_troubleshooter`)**:
    - **Role**: Execution specialist.
    - **Tools**: `execute_api_request`.
    - **Workflow**: Takes the troubleshooting guide from the planner and performs the actual API calls to diagnose the system.

## How it Works

1.  **User Report**: A user reports a symptom.
2.  **Retrieval**: The Planner agent searches for relevant troubleshooting guides and API documentation.
3.  **Planning**: The Planner generates a detailed troubleshooting guide specific to the symptom.
4.  **Delegation**: The Planner calls the Troubleshooter agent (via `AgentTool`).
5.  **Execution**: The Troubleshooter follows the guide, calls APIs, and generates a final report.
6.  **Resolution**: The system returns a comprehensive report of the findings.
