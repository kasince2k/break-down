#!/usr/bin/env python3
"""
Generate a sample Obsidian canvas file.

This script generates a sample Obsidian canvas file that demonstrates the structure
of the canvas files created by the Obsidian Article Breakdown Agent.
"""

import json
import uuid
from pathlib import Path


def generate_sample_canvas(output_path: str) -> None:
    """Generate a sample Obsidian canvas file.

    Args:
        output_path: Path to save the canvas file.
    """
    # Create nodes
    nodes = []
    edges = []

    # Original article node
    original_id = str(uuid.uuid4())
    nodes.append(
        {
            "id": original_id,
            "x": 0,
            "y": -600,
            "width": 300,
            "height": 200,
            "type": "file",
            "file": "Clippings/sample-article.md",
            "color": "6",  # Purple
        }
    )

    # Summary node
    summary_id = str(uuid.uuid4())
    nodes.append(
        {
            "id": summary_id,
            "x": 0,
            "y": -300,
            "width": 300,
            "height": 200,
            "type": "file",
            "file": "Understanding Markdown-Breakdown/00-Summary.md",
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

    # Main section nodes
    section_titles = [
        "Why Use Markdown",
        "Basic Syntax",
        "Advanced Markdown Features",
        "Markdown in Different Environments",
        "Best Practices",
        "Conclusion",
    ]

    # Calculate horizontal spacing
    total_width = len(section_titles) * 300 + (len(section_titles) - 1) * 200
    start_x = -total_width / 2

    section_ids = {}
    for i, title in enumerate(section_titles, 1):
        section_id = str(uuid.uuid4())
        x_pos = start_x + i * 500 - 500  # 300px width + 200px spacing

        nodes.append(
            {
                "id": section_id,
                "x": x_pos,
                "y": 0,
                "width": 300,
                "height": 200,
                "type": "file",
                "file": f"Understanding Markdown-Breakdown/{i:02d}-{title.replace(' ', '-')}.md",
                "color": "3",  # Yellow
            }
        )

        # Connect summary to this section
        edges.append(
            {
                "id": str(uuid.uuid4()),
                "fromNode": summary_id,
                "fromSide": "bottom",
                "toNode": section_id,
                "toSide": "top",
            }
        )

        section_ids[i] = (section_id, x_pos)

    # Subsection nodes for Basic Syntax
    subsection_titles = ["Headers", "Emphasis", "Lists", "Links", "Images"]

    for j, title in enumerate(subsection_titles, 1):
        subsection_id = str(uuid.uuid4())
        parent_id, parent_x = section_ids[2]  # Basic Syntax is section 2

        # Calculate x position based on number of subsections
        subsection_width = len(subsection_titles) * 300 + (len(subsection_titles) - 1) * 100
        subsection_start_x = parent_x - subsection_width / 2 + 150
        x_pos = subsection_start_x + (j - 1) * 400  # 300px width + 100px spacing

        nodes.append(
            {
                "id": subsection_id,
                "x": x_pos,
                "y": 300,
                "width": 300,
                "height": 200,
                "type": "file",
                "file": f"Understanding Markdown-Breakdown/02.{j:02d}-{title.replace(' ', '-')}.md",
                "color": "5",  # Cyan
            }
        )

        # Connect parent section to this subsection
        edges.append(
            {
                "id": str(uuid.uuid4()),
                "fromNode": parent_id,
                "fromSide": "bottom",
                "toNode": subsection_id,
                "toSide": "top",
            }
        )

    # Special node for References
    special_id = str(uuid.uuid4())
    nodes.append(
        {
            "id": special_id,
            "x": 800,
            "y": -300,
            "width": 300,
            "height": 200,
            "type": "file",
            "file": "Understanding Markdown-Breakdown/References.md",
            "color": "2",  # Orange
        }
    )

    # Connect summary to special node
    edges.append(
        {
            "id": str(uuid.uuid4()),
            "fromNode": summary_id,
            "fromSide": "right",
            "toNode": special_id,
            "toSide": "left",
        }
    )

    # Create canvas data
    canvas_data = {"nodes": nodes, "edges": edges}

    # Write canvas file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(canvas_data, f, indent=2)

    print(f"Sample canvas file generated at: {output_path}")


def main() -> None:
    """Main function."""
    # Create examples directory if it doesn't exist
    examples_dir = Path(__file__).parent
    output_path = examples_dir / "sample-canvas.canvas"

    generate_sample_canvas(str(output_path))

    print("\nTo use this sample canvas:")
    print("1. Copy it to your Obsidian vault")
    print("2. Open it in Obsidian to see the structure")
    print("3. Note that the file references won't work unless you have the corresponding files")


if __name__ == "__main__":
    main()
