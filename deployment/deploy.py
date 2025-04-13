#!/usr/bin/env python3
"""
Deployment script for the Obsidian Article Breakdown Agent.

This script deploys the agent to Vertex AI Agent Engine.
"""

import argparse
import os
from typing import Dict, Optional

from google.cloud import aiplatform
from google.cloud.aiplatform import Agent as VertexAgent

# Import the agent
from obsidian_article_breakdown import ObsidianArticleBreakdownAgent


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy the Obsidian Article Breakdown Agent")
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.environ.get("PROJECT_ID"),
        help="Google Cloud project ID",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=os.environ.get("LOCATION", "us-central1"),
        help="Google Cloud location",
    )
    parser.add_argument(
        "--display-name",
        type=str,
        default="Obsidian Article Breakdown Agent",
        help="Display name for the agent",
    )
    parser.add_argument(
        "--description",
        type=str,
        default="An agent that creates structured breakdowns of articles in Obsidian",
        help="Description of the agent",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("MODEL_NAME", "gemini-1.5-pro"),
        help="Model to use for the agent",
    )
    return parser.parse_args()


def init_vertex_ai(project_id: str, location: str) -> None:
    """Initialize Vertex AI with the given project and location.

    Args:
        project_id: Google Cloud project ID.
        location: Google Cloud location.
    """
    aiplatform.init(project=project_id, location=location)


def create_agent_config(display_name: str, description: str, model: str) -> Dict[str, str]:
    """Create the agent configuration.

    Args:
        display_name: Display name for the agent.
        description: Description of the agent.
        model: Model to use for the agent.

    Returns:
        Agent configuration dictionary.
    """
    return {
        "display_name": display_name,
        "description": description,
        "model": model,
    }


def deploy_agent(
    agent_config: Dict[str, str], project_id: str, location: str
) -> Optional[VertexAgent]:
    """Deploy the agent to Vertex AI Agent Engine.

    Args:
        agent_config: Agent configuration.
        project_id: Google Cloud project ID.
        location: Google Cloud location.

    Returns:
        The deployed agent or None if deployment failed.
    """
    try:
        # Create the agent
        agent = ObsidianArticleBreakdownAgent()

        # Convert to Vertex AI Agent
        vertex_agent = VertexAgent.from_adk_agent(
            adk_agent=agent,
            display_name=agent_config["display_name"],
            description=agent_config["description"],
            model=agent_config["model"],
        )

        # Deploy the agent
        vertex_agent = vertex_agent.deploy(project=project_id, location=location)

        print(f"Agent deployed successfully with ID: {vertex_agent.name}")
        print(
            f"Agent URL: https://console.cloud.google.com/vertex-ai/agents/{vertex_agent.name}?project={project_id}"
        )

        return vertex_agent
    except Exception as e:
        print(f"Error deploying agent: {str(e)}")
        return None


def main() -> None:
    """Main function to deploy the agent."""
    args = parse_args()

    # Validate required arguments
    if not args.project_id:
        raise ValueError(
            "Project ID is required. Set it with --project-id or PROJECT_ID environment variable."
        )

    # Initialize Vertex AI
    init_vertex_ai(args.project_id, args.location)

    # Create agent configuration
    agent_config = create_agent_config(args.display_name, args.description, args.model)

    # Deploy the agent
    deploy_agent(agent_config, args.project_id, args.location)


if __name__ == "__main__":
    main()
