# Tech Context

## Core Technologies
- **Language**: Python >= 3.11
- **Framework**: [Google ADK](https://github.com/google/adk) (Agent Development Kit)
- **AI Models**: Managed via `litellm` (configured for Gemini/Vertex AI).
- **Observability**: OpenTelemetry (SDK & OTLP exporter).
- **API Framework**: FastAPI (for the dummy service).

## Development Tools
- **Package Manager**: `uv` (Fast Python package installer and resolver).
- **Linting/Formatting**: `ruff`
- **Validation**: `pydantic` (with email support).
- **Execution**: `adk run` for executing agent entry points with tracing.

## Infrastructure
- **Containerization**: `docker-compose` for local development (Otel collector, backend service).
- **Tracing**: OTLP traces sent to `http://localhost:5000/v1/traces` by default.

## Technical Constraints
- Requires `GOOGLE_API_KEY` or Vertex AI credentials.
- Strictly adheres to the 4-layer architecture defined in `docs/adk-system-infrastructure-design-guideline.md`.
