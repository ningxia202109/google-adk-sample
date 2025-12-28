# Google ADK Sample

Sample projects using Google ADK framework for enterprise AI agentic applications.

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
