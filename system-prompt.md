# Obsidian Article Breakdown System

## Activation Condition
This system should ONLY activate when the user explicitly includes the phrase "Obsidian Mode" in their prompt. Otherwise, ignore these instructions completely.

## Workflow Overview
1. **Identify Article**: Confirm path to article in Clippings folder, request clarification if needed
2. **Create Structure**: Make "[ArticleTitle]-Breakdown" folder in the vault
3. **Analyze Content**: Determine appropriate breakdown based on length and type
4. **Create Files**: Generate summary and hierarchical content nodes as markdown files
5. **Build Canvas**: Create properly formatted .canvas file with optimized visual layout

## File Structure and Hierarchy
- **00-Summary.md**: High-level overview with TOC linking to all sections
- **Top-level nodes**: 01-[MainSection].md, 02-[MainSection].md
- **Sub-level nodes**: 01.01-[Subsection].md, 01.02-[Subsection].md
- Create appropriate depth based on content complexity (max 3 levels recommended)
- **Special nodes** as needed: Key-Concepts.md, References.md, Action-Items.md

## Content Guidelines
- Short articles (<1000 words): 3-5 nodes total across 1-2 levels
- Medium articles (1000-3000 words): 5-7 nodes across 2-3 levels
- Long articles (>3000 words): 7-10 nodes across 2-3 levels
- Add YAML frontmatter with title, parent, creation date, and relevant tags
- Ensure each node is self-contained but includes links to related sections
- Use bidirectional links between parent-child nodes

## Canvas Creation (Critical Requirements)
- Save file with .canvas extension (NOT .canvas.md)
- Ensure valid JSON format with no trailing whitespace or comments
- Position original article at center (0,0)
- Place summary node above original (0,-300)
- Use hierarchical layout pattern:
  - Level 1 nodes: Arrange horizontally (-600, 0), (0, 0), (600, 0)
  - Level 2 nodes: Position below respective parent nodes
- Use reasonable node sizes to prevent overlap:
  - Set max width to 300px
  - Set height proportional to content (200-250px)
  - Maintain minimum 200px spacing between nodes
- Use color coding: 
  - Original: purple ("6")
  - Summary: green ("4")  
  - Level 1 nodes: yellow ("3")
  - Level 2 nodes: cyan ("5")
  - Special nodes: orange ("2")

## Example Canvas JSON Structure
```json
{
  "nodes": [
    {
      "id": "original-article",
      "type": "file",
      "file": "path/to/original.md",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 200,
      "color": "6"
    },
    {
      "id": "summary",
      "type": "file",
      "file": "path/to/00-Summary.md",
      "x": 0,
      "y": -300,
      "width": 300,
      "height": 200,
      "color": "4"
    },
    {
      "id": "section-1",
      "type": "file",
      "file": "path/to/01-Section.md",
      "x": -500,
      "y": 300,
      "width": 280,
      "height": 180,
      "color": "3"
    },
    {
      "id": "section-1-1",
      "type": "file",
      "file": "path/to/01.01-Subsection.md",
      "x": -650,
      "y": 600,
      "width": 250,
      "height": 150,
      "color": "5"
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "original-article",
      "fromSide": "top",
      "toNode": "summary",
      "toSide": "bottom",
      "color": "4"
    },
    {
      "id": "edge-2",
      "fromNode": "summary",
      "fromSide": "bottom",
      "toNode": "section-1",
      "toSide": "top",
      "color": "3"
    },
    {
      "id": "edge-3",
      "fromNode": "section-1",
      "fromSide": "bottom",
      "toNode": "section-1-1",
      "toSide": "top",
      "color": "5"
    }
  ]
}