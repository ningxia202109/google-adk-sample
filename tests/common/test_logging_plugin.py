import unittest
from unittest.mock import MagicMock, patch
import structlog
from src.common.logging_plugin import StructuredLoggingPlugin
from google.adk.agents.invocation_context import InvocationContext

class TestStructuredLoggingPlugin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.plugin = StructuredLoggingPlugin()
        # Mock InvocationContext with appropriate attributes
        self.mock_context = MagicMock()
        self.mock_context.invocation_id = "test-invocation-id"
        self.mock_context.agent = MagicMock()
        self.mock_context.agent.name = "TestAgent"

    @patch("structlog.contextvars.bind_contextvars")
    @patch("structlog.get_logger")
    async def test_before_run_callback(self, mock_get_logger, mock_bind):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        # Re-initialize plugin to use mocked logger
        self.plugin = StructuredLoggingPlugin()

        await self.plugin.before_run_callback(invocation_context=self.mock_context)

        mock_bind.assert_called_once_with(correlation_id="test-invocation-id")
        self.plugin.logger.info.assert_called_with(
            "agent_run_started",
            agent_name="TestAgent",
            correlation_id="test-invocation-id",
        )

    @patch("structlog.contextvars.clear_contextvars")
    async def test_after_run_callback(self, mock_clear):
        self.plugin.logger = MagicMock()
        await self.plugin.after_run_callback(invocation_context=self.mock_context)

        self.plugin.logger.info.assert_called_with(
            "agent_run_completed",
            agent_name="TestAgent",
            correlation_id="test-invocation-id",
        )
        mock_clear.assert_called_once()

    async def test_before_run_callback_no_invocation_id(self):
        # Simulate missing invocation_id
        del self.mock_context.invocation_id
        self.plugin.logger = MagicMock()

        with patch("structlog.contextvars.bind_contextvars") as mock_bind:
            await self.plugin.before_run_callback(invocation_context=self.mock_context)
            mock_bind.assert_called_once_with(correlation_id="unknown")

if __name__ == "__main__":
    unittest.main()
