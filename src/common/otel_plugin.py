from typing import Any, Optional
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext

exporter = OTLPSpanExporter(
    endpoint="http://localhost:5000/v1/traces",
    headers={"x-mlflow-experiment-id": "4"},
)

provider = TracerProvider()


class OtelTracingPlugin(BasePlugin):
    """
    A plugin that initializes OpenTelemetry tracing and ensures spans are exported.
    """

    def __init__(self, name: str = "otel_tracing"):
        super().__init__(name=name)
        # Initialize the tracer provider with the batch processor
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[Any]:
        # You could start a root span here if desired,
        # but ADK already has internal OTel instrumentation.
        # This plugin mainly serves to ensure the provider is configured.
        return None

    async def after_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> None:
        # Force flush to ensure all spans are sent after a run
        provider.force_flush()

    async def close(self) -> None:
        # Shutdown the provider when the runner is closed
        provider.shutdown()
