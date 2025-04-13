# Obsidian Article Breakdown System

## Activation Condition

This system activates when the user includes "Obsidian Mode" in their prompt.

## Workflow Overview

1. **Identify Article**: Confirm path to article in Clippings folder
2. **Create Structure**: Make "[ArticleTitle]-Breakdown" folder in the vault
3. **Analyze Content**: Create comprehensive breakdown preserving original content and tone
4. **Create Files**: Generate summary and hierarchical content nodes as markdown files
5. **Build Canvas**: Create properly formatted .canvas file with inverted tree structure and optimized visual layout

## File Structure and Hierarchy

- **00-Summary.md**: High-level overview with TOC linking to all sections
- **Top-level nodes**: 01-[MainSection].md, 02-[MainSection].md, etc.
- **Sub-level nodes**: Required for all articles >1000 words (01.01-[Subsection].md, 01.02-[Subsection].md)
- Create appropriate depth based on content complexity (max 3 levels recommended)
- **Special nodes** as needed: Key-Concepts.md, References.md, Action-Items.md

## Content Guidelines

- Short articles (<1000 words): 3-5 nodes total across 1-2 levels
- Medium articles (1000-3000 words): 5-8 nodes across 2-3 levels with REQUIRED subsections
- Long articles (>3000 words): 8-12 nodes across 3 levels with REQUIRED subsections
- Add YAML frontmatter with title, parent, creation date, original article, and relevant tags
- Preserve original content and tone - focus on organizing not summarizing
- Include substantial direct quotes from the original text
- Ensure each node is self-contained but includes links to related sections
- Use bidirectional links between parent-child nodes

## Canvas Creation (Critical Requirements)

- Use inverted tree structure with original article at top (0,-600)
- Place summary node below original (0,-300)
- Level 1 nodes below summary in horizontal arrangement
- Level 2/3 nodes below their respective parents
- Node positioning guide:
  - Original article: (0,-600)
  - Summary: (0,-300)
  - Level 1 nodes: Spread horizontally at y=0, x positions spaced evenly
  - Level 2 nodes: Below respective parent nodes at y=300
  - Level 3 nodes: Below respective parent nodes at y=600
- Use reasonable node sizes: width=300px, height proportional to content (200-300px)
- Maintain minimum 200px spacing between nodes at same level
- Color coding:
  - Original: purple ("6")
  - Summary: green ("4")
  - Level 1 nodes: yellow ("3")
  - Level 2 nodes: cyan ("5")
  - Level 3 nodes: blue ("1")
  - Special nodes: orange ("2")

## Canvas File Creation Instructions

1. Create a standard .canvas file (not .canvas.md)
2. Structure with "nodes" and "edges" arrays
3. Each node requires: unique id, file path, x/y coordinates, width/height, color
4. Connect nodes with edges defining: id, source node, target node, from/to sides, color
5. Ensure valid JSON format with no trailing whitespace or comments

## Tool Usage

Use the appropriate Obsidian tools to:

- Read and analyze the original article content
- Create necessary folder structure and markdown files
- Build and save the .canvas file with correct structure
- Reference all files with their complete paths relative to vault root
