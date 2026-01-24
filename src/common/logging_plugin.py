import structlog
from typing import Any, Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20), # INFO
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

class StructuredLoggingPlugin(BasePlugin):
    """
    A plugin that adds structured logging to the agent run.
    It captures correlation_id from the invocation context.
    """

    def __init__(self, name: str = "structured_logging"):
        super().__init__(name=name)
        self.logger = structlog.get_logger()

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[Any]:
        # Bind correlation_id to the logger context
        correlation_id = invocation_context.correlation_id or "unknown"
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        self.logger.info(
            "agent_run_started",
            agent_name=invocation_context.agent_name,
            correlation_id=correlation_id
        )
        return None

    async def after_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> None:
        self.logger.info(
            "agent_run_completed",
            agent_name=invocation_context.agent_name,
            correlation_id=invocation_context.correlation_id or "unknown"
        )
        # Clear contextvars after run
        structlog.contextvars.clear_contextvars()

    async def close(self) -> None:
        pass
