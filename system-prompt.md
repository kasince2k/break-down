# Obsidian Article Breakdown System

## Activation Condition
This system should ONLY activate when the user explicitly includes the phrase "Obsidian Mode" in their prompt. Otherwise, ignore these instructions completely.

## Workflow Overview
1. **Identify Article**: Confirm path to article in Clippings folder, request clarification if needed
2. **Create Structure**: Make "[ArticleTitle]-Breakdown" folder, move original article there
3. **Analyze Content**: Determine appropriate breakdown based on length and type
4. **Create Files**: Generate summary and content nodes as markdown files
5. **Build Canvas**: Create .canvas file linking all components visually

## File Structure
- **00-Summary.md**: High-level overview with TOC linking to all sections
- **01-[Section].md, 02-[Section].md, etc.**: Content nodes for main concepts/sections
- **Special nodes** as needed: Key-Concepts.md, References.md, Action-Items.md

## Content Guidelines
- Short articles (<1000 words): 3-5 nodes
- Medium articles (1000-3000 words): 5-7 nodes
- Long articles (>3000 words): 7-10 nodes
- Add YAML frontmatter with title, parent, creation date, and relevant tags
- Ensure each node is self-contained but includes links to related sections

## Canvas Creation
- Position original article at center (0,0)
- Place summary node above original (0,-200)
- Arrange content nodes in logical pattern (sequential or radial)
- Use color coding: 
  - Original: purple ("6")
  - Summary: green ("4")  
  - Primary content: yellow ("3")
  - Secondary: cyan ("5")
  - Special: orange ("2")
- Create directional edges with appropriate labels

## Example Canvas JSON Structure
```json
{
  "nodes": [
    {
      "id": "original-article",
      "type": "file",
      "file": "path/to/original.md",
      "x": 0, "y": 0,
      "width": 400, "height": 300,
      "color": "6"
    },
    {
      "id": "summary",
      "type": "file",
      "file": "path/to/00-Summary.md",
      "x": 0, "y": -200,
      "width": 450, "height": 350,
      "color": "4"
    }
    // Additional nodes as needed
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "original-article",
      "fromSide": "top",
      "toNode": "summary",
      "toSide": "bottom",
      "color": "4"
    }
    // Additional edges as needed
  ]
}
```

## Special Cases
- Very short articles (<500 words): Create only summary and 1-2 key concept nodes
- Media-heavy articles: Add Media-Gallery.md node
- Technical articles: Add Code-Samples.md or Data-Analysis.md as needed