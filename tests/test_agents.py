"""Tests for the Obsidian Article Breakdown Agent."""

import unittest
from unittest.mock import MagicMock, patch

from google.adk import Message, MessageType
from google.adk.tool import ToolResponse

from obsidian_article_breakdown import ObsidianArticleBreakdownAgent


class TestObsidianArticleBreakdownAgent(unittest.TestCase):
    """Test cases for the Obsidian Article Breakdown Agent."""

    def setUp(self):
        """Set up the test environment."""
        self.agent = ObsidianArticleBreakdownAgent()
        self.context = MagicMock()

        # Mock the LLM response
        self.llm_response = MagicMock()
        self.llm_response.success = True
        self.llm_response.text = """
# Summary
This is a summary of the article.

# Section 1
This is the content of section 1.

## Subsection 1.1
This is the content of subsection 1.1.

# Section 2
This is the content of section 2.

# Special: Key Concepts
These are the key concepts.
"""
        self.context.llm.generate_content.return_value = self.llm_response

        # Mock the MCP tool responses
        self.tool_response = MagicMock(spec=ToolResponse)
        self.tool_response.success = True
        self.tool_response.result = {"content": "# Test Article\n\nThis is a test article."}
        self.context.use_mcp_tool.return_value = self.tool_response

    def test_get_system_prompt(self):
        """Test that the system prompt is returned correctly."""
        prompt = self.agent.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("Obsidian Article Breakdown System", prompt)

    def test_activation_phrase(self):
        """Test that the agent responds to the activation phrase."""
        # Test with activation phrase
        message = Message.from_text("Obsidian Mode\nPlease process article: test.md")
        response = self.agent.process(message, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.type, MessageType.TEXT)

        # Test without activation phrase
        message = Message.from_text("Please process article: test.md")
        response = self.agent.process(message, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.type, MessageType.TEXT)
        self.assertIn("To activate the Obsidian Article Breakdown System", response.text)

    def test_extract_article_path(self):
        """Test the article path extraction."""
        # Test with explicit path indicator
        path = self.agent._extract_article_path("path: /path/to/article.md")
        self.assertEqual(path, "/path/to/article.md")

        # Test with article indicator
        path = self.agent._extract_article_path("article: /path/to/article.md")
        self.assertEqual(path, "/path/to/article.md")

        # Test with path in text
        path = self.agent._extract_article_path("Please process the article at /path/to/article.md")
        self.assertEqual(path, "/path/to/article.md")

        # Test with no path
        path = self.agent._extract_article_path("Please process this article")
        self.assertIsNone(path)

    @patch.object(ObsidianArticleBreakdownAgent, "_process_article_breakdown")
    def test_process_with_path(self, mock_process):
        """Test processing with a valid path."""
        mock_process.return_value = "Article breakdown complete!"

        message = Message.from_text("Obsidian Mode\npath: /path/to/article.md")
        response = self.agent.process(message, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.type, MessageType.TEXT)
        self.assertEqual(response.text, "Article breakdown complete!")
        mock_process.assert_called_once_with("/path/to/article.md", self.context)

    @patch.object(ObsidianArticleBreakdownAgent, "_process_article_breakdown")
    def test_process_without_path(self, mock_process):
        """Test processing without a path."""
        message = Message.from_text("Obsidian Mode")
        response = self.agent.process(message, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.type, MessageType.TEXT)
        self.assertIn("Please provide a path", response.text)
        mock_process.assert_not_called()

    @patch.object(ObsidianArticleBreakdownAgent, "_process_article_breakdown")
    def test_process_with_error(self, mock_process):
        """Test processing with an error."""
        mock_process.side_effect = Exception("Test error")

        message = Message.from_text("Obsidian Mode\npath: /path/to/article.md")
        response = self.agent.process(message, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.type, MessageType.TEXT)
        self.assertIn("An error occurred", response.text)
        self.assertIn("Test error", response.text)
        mock_process.assert_called_once_with("/path/to/article.md", self.context)


if __name__ == "__main__":
    unittest.main()
