"""Obsidian Article Breakdown Agent implementation."""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk import Agent, AgentContext, Message, MessageType
from google.adk.llm import LlmResponse
from google.adk.tool import Tool, ToolResponse

from obsidian_article_breakdown.prompt import (
    ARTICLE_ANALYSIS_PROMPT,
    SYSTEM_PROMPT,
)


class ObsidianArticleBreakdownAgent(Agent):
    """Agent that creates structured breakdowns of articles in Obsidian."""

    def __init__(self) -> None:
        """Initialize the Obsidian Article Breakdown Agent."""
        super().__init__()
        self.obsidian_mcp_server = "obsidian-mcp"
        self.article_path = None
        self.article_content = None
        self.article_title = None
        self.breakdown_folder = None
        self.created_files = []

    def get_tools(self) -> List[Tool]:
        """Return the tools available to the agent."""
        return []

    def get_system_prompt(self) -> str:
        """Return the system prompt for the agent."""
        return SYSTEM_PROMPT

    def process(self, message: Message, context: AgentContext) -> Optional[Message]:
        """Process the user message and create an article breakdown in Obsidian.

        Args:
            message: The user message to process.
            context: The agent context.

        Returns:
            A response message or None if no response is needed.
        """
        # Check if the message contains "Obsidian Mode" activation phrase
        if message.type == MessageType.TEXT and "Obsidian Mode" in message.text:
            # Extract article path from the message if provided
            article_path = self._extract_article_path(message.text)
            if not article_path:
                return Message.from_text(
                    "Please provide a path to the article in your Obsidian vault's Clippings folder."
                )

            # Process the article breakdown
            try:
                result = self._process_article_breakdown(article_path, context)
                return Message.from_text(result)
            except Exception as e:
                return Message.from_text(
                    f"An error occurred while processing the article breakdown: {str(e)}"
                )

        # If "Obsidian Mode" is not in the message, provide instructions
        return Message.from_text(
            "To activate the Obsidian Article Breakdown System, please include 'Obsidian Mode' "
            "in your message along with the path to the article in your Obsidian vault."
        )

    def _extract_article_path(self, message_text: str) -> Optional[str]:
        """Extract the article path from the user message.

        Args:
            message_text: The text of the user message.

        Returns:
            The extracted article path or None if not found.
        """
        # Simple extraction logic - can be enhanced with regex or more sophisticated parsing
        lines = message_text.split("\n")
        for line in lines:
            if "path:" in line.lower() or "article:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()

        # If no explicit path indicator, look for file paths
        for line in lines:
            if ".md" in line and "/" in line:
                # Extract potential file path
                words = line.split()
                for word in words:
                    if ".md" in word:
                        return word.strip()

        return None

    def _process_article_breakdown(self, article_path: str, context: AgentContext) -> str:
        """Process the article breakdown workflow.

        Args:
            article_path: The path to the article in the Obsidian vault.
            context: The agent context.

        Returns:
            A message describing the result of the article breakdown process.
        """
        # Step 1: Identify Article - Read the article content using the MCP server
        self.article_path = article_path
        self.article_content = self._read_article_content(article_path, context)
        if not self.article_content:
            return f"Could not read the article at {article_path}. Please check the path and try again."

        # Extract article title from the path or content
        self.article_title = self._extract_article_title(article_path, self.article_content)

        # Step 2: Create Structure - Create the breakdown folder
        self.breakdown_folder = f"{self.article_title}-Breakdown"
        self._create_folder(self.breakdown_folder, context)

        # Step 3: Analyze Content - Use LLM to analyze the article content
        analysis_result = self._analyze_article_content(self.article_content, context)

        # Step 4: Create Files - Generate markdown files based on the analysis
        self._create_markdown_files(analysis_result, context)

        # Step 5: Build Canvas - Create the canvas file
        canvas_path = self._create_canvas_file(context)

        return (
            f"Article breakdown complete!\n\n"
            f"Created breakdown folder: {self.breakdown_folder}\n"
            f"Generated {len(self.created_files)} markdown files\n"
            f"Created canvas visualization: {canvas_path}\n\n"
            f"You can now open the canvas file in Obsidian to view the structured breakdown."
        )

    def _read_article_content(self, article_path: str, context: AgentContext) -> Optional[str]:
        """Read the article content using the obsidian-mcp server.

        Args:
            article_path: The path to the article in the Obsidian vault.
            context: The agent context.

        Returns:
            The article content or None if it couldn't be read.
        """
        try:
            # Use the MCP server to read the file
            response = context.use_mcp_tool(
                server_name=self.obsidian_mcp_server,
                tool_name="read_file",
                arguments={"path": article_path},
            )

            if isinstance(response, ToolResponse) and response.success:
                return response.result.get("content")
            return None
        except Exception as e:
            print(f"Error reading article content: {str(e)}")
            return None

    def _extract_article_title(self, article_path: str, content: str) -> str:
        """Extract the article title from the path or content.

        Args:
            article_path: The path to the article.
            content: The article content.

        Returns:
            The extracted article title.
        """
        # Try to extract from filename first
        filename = os.path.basename(article_path)
        if filename.endswith(".md"):
            filename = filename[:-3]  # Remove .md extension
            return filename

        # If filename doesn't work, try to extract from the first heading in the content
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()

        # If all else fails, use a generic title with timestamp
        return f"Article-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _create_folder(self, folder_name: str, context: AgentContext) -> bool:
        """Create a folder in the Obsidian vault using the MCP server.

        Args:
            folder_name: The name of the folder to create.
            context: The agent context.

        Returns:
            True if the folder was created successfully, False otherwise.
        """
        try:
            response = context.use_mcp_tool(
                server_name=self.obsidian_mcp_server,
                tool_name="create_folder",
                arguments={"path": folder_name},
            )

            return isinstance(response, ToolResponse) and response.success
        except Exception as e:
            print(f"Error creating folder: {str(e)}")
            return False

    def _analyze_article_content(self, content: str, context: AgentContext) -> Dict[str, Any]:
        """Analyze the article content using the LLM.

        Args:
            content: The article content to analyze.
            context: The agent context.

        Returns:
            A dictionary containing the analysis results.
        """
        prompt = ARTICLE_ANALYSIS_PROMPT.format(article_content=content)

        # Use the LLM to analyze the content
        llm_response = context.llm.generate_content(prompt)

        if isinstance(llm_response, LlmResponse) and llm_response.success:
            # Parse the LLM response to extract the structured breakdown
            return self._parse_analysis_response(llm_response.text)

        # Return a default structure if analysis fails
        return {
            "summary": "Summary of the article",
            "sections": [
                {"title": "Section 1", "content": "Content of section 1", "subsections": []},
                {"title": "Section 2", "content": "Content of section 2", "subsections": []},
            ],
            "special_nodes": [],
        }

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM analysis response into a structured format.

        Args:
            response_text: The text response from the LLM.

        Returns:
            A dictionary containing the parsed analysis.
        """
        # This is a simplified parsing logic - in a real implementation,
        # you would need more robust parsing based on the LLM's output format
        lines = response_text.split("\n")

        result = {"summary": "", "sections": [], "special_nodes": []}

        current_section = None
        current_subsection = None

        for line in lines:
            if line.startswith("# Summary"):
                # Extract summary section
                summary_start = lines.index(line)
                summary_end = next(
                    (
                        i
                        for i, l in enumerate(lines[summary_start + 1 :], summary_start + 1)
                        if l.startswith("# ")
                    ),
                    len(lines),
                )
                result["summary"] = "\n".join(lines[summary_start + 1 : summary_end]).strip()

            elif line.startswith("# ") and not line.startswith("# Summary"):
                # Start a new main section
                title = line[2:].strip()
                current_section = {"title": title, "content": "", "subsections": []}
                result["sections"].append(current_section)
                current_subsection = None

            elif line.startswith("## ") and current_section is not None:
                # Start a new subsection
                title = line[3:].strip()
                current_subsection = {"title": title, "content": ""}
                current_section["subsections"].append(current_subsection)

            elif line.startswith("# Special: "):
                # Handle special nodes
                title = line[10:].strip()
                special_node = {"title": title, "content": ""}
                result["special_nodes"].append(special_node)
                current_section = None
                current_subsection = None

            elif current_subsection is not None:
                # Add content to current subsection
                current_subsection["content"] += line + "\n"

            elif current_section is not None:
                # Add content to current section
                current_section["content"] += line + "\n"

        return result

    def _create_markdown_files(self, analysis: Dict[str, Any], context: AgentContext) -> None:
        """Create markdown files based on the analysis results.

        Args:
            analysis: The analysis results.
            context: The agent context.
        """
        # Create summary file
        summary_path = f"{self.breakdown_folder}/00-Summary.md"
        summary_content = self._create_summary_content(analysis)
        self._write_file(summary_path, summary_content, context)
        self.created_files.append(summary_path)

        # Create section files
        for i, section in enumerate(analysis["sections"], 1):
            section_filename = f"{i:02d}-{self._sanitize_filename(section['title'])}.md"
            section_path = f"{self.breakdown_folder}/{section_filename}"

            section_content = self._create_section_content(section, i, summary_path)
            self._write_file(section_path, section_content, context)
            self.created_files.append(section_path)

            # Create subsection files if any
            for j, subsection in enumerate(section["subsections"], 1):
                subsection_filename = (
                    f"{i:02d}.{j:02d}-{self._sanitize_filename(subsection['title'])}.md"
                )
                subsection_path = f"{self.breakdown_folder}/{subsection_filename}"

                subsection_content = self._create_subsection_content(subsection, section_path, i, j)
                self._write_file(subsection_path, subsection_content, context)
                self.created_files.append(subsection_path)

        # Create special node files
        for special in analysis["special_nodes"]:
            special_filename = f"{self._sanitize_filename(special['title'])}.md"
            special_path = f"{self.breakdown_folder}/{special_filename}"

            special_content = self._create_special_node_content(special)
            self._write_file(special_path, special_content, context)
            self.created_files.append(special_path)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be used as a filename.

        Args:
            filename: The filename to sanitize.

        Returns:
            The sanitized filename.
        """
        # Replace invalid characters with hyphens
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        for char in invalid_chars:
            filename = filename.replace(char, "-")
        return filename

    def _create_summary_content(self, analysis: Dict[str, Any]) -> str:
        """Create the content for the summary file.

        Args:
            analysis: The analysis results.

        Returns:
            The content for the summary file.
        """
        now = datetime.now().strftime("%Y-%m-%d")

        content = f"""---
title: Summary of {self.article_title}
date: {now}
original_article: {self.article_path}
tags: [summary, article-breakdown]
---

# Summary

{analysis["summary"]}

## Table of Contents

"""

        # Add links to sections
        for i, section in enumerate(analysis["sections"], 1):
            section_filename = f"{i:02d}-{self._sanitize_filename(section['title'])}.md"
            content += f"- [[{section_filename}|{section['title']}]]\n"

            # Add links to subsections if any
            if section["subsections"]:
                content += (
                    "  - "
                    + " | ".join(
                        [
                            f"[[{i:02d}.{j:02d}-{self._sanitize_filename(subsection['title'])}.md|{subsection['title']}]]"
                            for j, subsection in enumerate(section["subsections"], 1)
                        ]
                    )
                    + "\n"
                )

        # Add links to special nodes if any
        if analysis["special_nodes"]:
            content += "\n## Special Nodes\n\n"
            for special in analysis["special_nodes"]:
                special_filename = f"{self._sanitize_filename(special['title'])}.md"
                content += f"- [[{special_filename}|{special['title']}]]\n"

        return content

    def _create_section_content(
        self, section: Dict[str, Any], section_num: int, summary_path: str
    ) -> str:
        """Create the content for a section file.

        Args:
            section: The section data.
            section_num: The section number.
            summary_path: The path to the summary file.

        Returns:
            The content for the section file.
        """
        now = datetime.now().strftime("%Y-%m-%d")
        summary_filename = os.path.basename(summary_path)

        content = f"""---
title: {section["title"]}
date: {now}
parent: [[{summary_filename}]]
original_article: {self.article_path}
tags: [section, article-breakdown]
---

# {section["title"]}

{section["content"]}

"""

        # Add links to subsections if any
        if section["subsections"]:
            content += "## Subsections\n\n"
            for j, subsection in enumerate(section["subsections"], 1):
                subsection_filename = (
                    f"{section_num:02d}.{j:02d}-{self._sanitize_filename(subsection['title'])}.md"
                )
                content += f"- [[{subsection_filename}|{subsection['title']}]]\n"

        # Add link back to summary
        content += f"\n[[{summary_filename}|Back to Summary]]\n"

        return content

    def _create_subsection_content(
        self, subsection: Dict[str, Any], parent_path: str, section_num: int, subsection_num: int
    ) -> str:
        """Create the content for a subsection file.

        Args:
            subsection: The subsection data.
            parent_path: The path to the parent section file.
            section_num: The section number.
            subsection_num: The subsection number.

        Returns:
            The content for the subsection file.
        """
        now = datetime.now().strftime("%Y-%m-%d")
        parent_filename = os.path.basename(parent_path)

        content = f"""---
title: {subsection["title"]}
date: {now}
parent: [[{parent_filename}]]
original_article: {self.article_path}
tags: [subsection, article-breakdown]
---

# {subsection["title"]}

{subsection["content"]}

[[{parent_filename}|Back to {parent_filename[3:-3]}]]
"""

        return content

    def _create_special_node_content(self, special: Dict[str, Any]) -> str:
        """Create the content for a special node file.

        Args:
            special: The special node data.

        Returns:
            The content for the special node file.
        """
        now = datetime.now().strftime("%Y-%m-%d")

        content = f"""---
title: {special["title"]}
date: {now}
original_article: {self.article_path}
tags: [special-node, article-breakdown]
---

# {special["title"]}

{special["content"]}

"""

        return content

    def _write_file(self, path: str, content: str, context: AgentContext) -> bool:
        """Write content to a file using the MCP server.

        Args:
            path: The path to write to.
            content: The content to write.
            context: The agent context.

        Returns:
            True if the file was written successfully, False otherwise.
        """
        try:
            response = context.use_mcp_tool(
                server_name=self.obsidian_mcp_server,
                tool_name="write_file",
                arguments={"path": path, "content": content},
            )

            return isinstance(response, ToolResponse) and response.success
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False

    def _create_canvas_file(self, context: AgentContext) -> str:
        """Create the canvas file for the article breakdown.

        Args:
            context: The agent context.

        Returns:
            The path to the created canvas file.
        """
        canvas_path = f"{self.breakdown_folder}/{self.article_title}-Breakdown.canvas"

        # Generate the canvas JSON structure
        canvas_data = self._generate_canvas_data()

        # Write the canvas file
        self._write_file(canvas_path, json.dumps(canvas_data, indent=2), context)

        return canvas_path

    def _generate_canvas_data(self) -> Dict[str, Any]:
        """Generate the canvas data structure.

        Returns:
            A dictionary containing the canvas data.
        """
        nodes = []
        edges = []

        # Add original article node
        original_id = str(uuid.uuid4())
        nodes.append(
            {
                "id": original_id,
                "x": 0,
                "y": -600,
                "width": 300,
                "height": 200,
                "type": "file",
                "file": self.article_path,
                "color": "6",  # Purple
            }
        )

        # Add summary node
        summary_path = f"{self.breakdown_folder}/00-Summary.md"
        summary_id = str(uuid.uuid4())
        nodes.append(
            {
                "id": summary_id,
                "x": 0,
                "y": -300,
                "width": 300,
                "height": 200,
                "type": "file",
                "file": summary_path,
                "color": "4",  # Green
            }
        )

        # Connect original to summary
        edges.append(
            {
                "id": str(uuid.uuid4()),
                "fromNode": original_id,
                "fromSide": "bottom",
                "toNode": summary_id,
                "toSide": "top",
            }
        )

        # Calculate positions for level 1 nodes (main sections)
        level1_nodes = [
            f
            for f in self.created_files
            if f.endswith(".md")
            and "/" in f
            and os.path.basename(f).startswith(
                ("01-", "02-", "03-", "04-", "05-", "06-", "07-", "08-", "09-")
            )
        ]

        if level1_nodes:
            # Calculate horizontal spacing
            total_width = len(level1_nodes) * 300 + (len(level1_nodes) - 1) * 200
            start_x = -total_width / 2

            # Add level 1 nodes
            level1_ids = {}
            for i, node_path in enumerate(level1_nodes):
                node_id = str(uuid.uuid4())
                x_pos = start_x + i * 500  # 300px width + 200px spacing

                nodes.append(
                    {
                        "id": node_id,
                        "x": x_pos,
                        "y": 0,
                        "width": 300,
                        "height": 200,
                        "type": "file",
                        "file": node_path,
                        "color": "3",  # Yellow
                    }
                )

                # Connect summary to this node
                edges.append(
                    {
                        "id": str(uuid.uuid4()),
                        "fromNode": summary_id,
                        "fromSide": "bottom",
                        "toNode": node_id,
                        "toSide": "top",
                    }
                )

                # Store the ID for connecting subsections
                level1_ids[node_path] = (node_id, x_pos)

            # Add level 2 nodes (subsections)
            level2_nodes = [
                f
                for f in self.created_files
                if f.endswith(".md")
                and "/" in f
                and "." in os.path.basename(f)
                and os.path.basename(f)[3] == "."
            ]

            for node_path in level2_nodes:
                # Find the parent section
                parent_num = os.path.basename(node_path)[:2]
                parent_path = next(
                    (p for p in level1_nodes if os.path.basename(p).startswith(parent_num + "-")),
                    None,
                )

                if parent_path and parent_path in level1_ids:
                    parent_id, parent_x = level1_ids[parent_path]

                    # Create the subsection node
                    node_id = str(uuid.uuid4())
                    nodes.append(
                        {
                            "id": node_id,
                            "x": parent_x,
                            "y": 300,
                            "width": 300,
                            "height": 200,
                            "type": "file",
                            "file": node_path,
                            "color": "5",  # Cyan
                        }
                    )

                    # Connect to parent
                    edges.append(
                        {
                            "id": str(uuid.uuid4()),
                            "fromNode": parent_id,
                            "fromSide": "bottom",
                            "toNode": node_id,
                            "toSide": "top",
                        }
                    )

        # Add special nodes if any
        special_nodes = [
            f
            for f in self.created_files
            if f.endswith(".md")
            and "/" in f
            and not os.path.basename(f).startswith(
                ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
            )
        ]

        if special_nodes:
            # Position special nodes to the right of the main structure
            special_x = 800
            special_y = -300

            for node_path in special_nodes:
                node_id = str(uuid.uuid4())
                nodes.append(
                    {
                        "id": node_id,
                        "x": special_x,
                        "y": special_y,
                        "width": 300,
                        "height": 200,
                        "type": "file",
                        "file": node_path,
                        "color": "2",  # Orange
                    }
                )

                # Connect to summary
                edges.append(
                    {
                        "id": str(uuid.uuid4()),
                        "fromNode": summary_id,
                        "fromSide": "right",
                        "toNode": node_id,
                        "toSide": "left",
                    }
                )

                special_y += 250  # Move down for next special node

        return {"nodes": nodes, "edges": edges}
