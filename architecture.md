# Obsidian Article Breakdown Agent Architecture

This document describes the architecture and workflow of the Obsidian Article Breakdown Agent.

## Architecture Diagram

```mermaid
graph TD
    User[User] -->|"Sends message with 'Obsidian Mode'"| Agent[Obsidian Article Breakdown Agent]
    
    subgraph "Agent Components"
        Agent -->|Processes request| Workflow[Workflow Engine]
        Workflow -->|Step 1| Identify[Identify Article]
        Workflow -->|Step 2| Structure[Create Structure]
        Workflow -->|Step 3| Analyze[Analyze Content]
        Workflow -->|Step 4| Files[Create Files]
        Workflow -->|Step 5| Canvas[Build Canvas]
    end
    
    subgraph "MCP Server"
        MCPServer[Obsidian MCP Server]
        MCPTools[MCP Tools]
        MCPServer -->|Provides| MCPTools
        MCPTools -->|read_file| ReadFile[Read File Tool]
        MCPTools -->|write_file| WriteFile[Write File Tool]
        MCPTools -->|create_folder| CreateFolder[Create Folder Tool]
        MCPTools -->|list_files| ListFiles[List Files Tool]
        MCPTools -->|search_vault| SearchVault[Search Vault Tool]
    end
    
    Agent <-->|Uses MCP tools| MCPServer
    
    subgraph "Obsidian Vault"
        Vault[Obsidian Vault]
        Article[Original Article]
        BreakdownFolder[Breakdown Folder]
        SummaryFile[Summary File]
        SectionFiles[Section Files]
        SubsectionFiles[Subsection Files]
        CanvasFile[Canvas File]
        
        Vault -->|Contains| Article
        Vault -->|Contains| BreakdownFolder
        BreakdownFolder -->|Contains| SummaryFile
        BreakdownFolder -->|Contains| SectionFiles
        BreakdownFolder -->|Contains| SubsectionFiles
        BreakdownFolder -->|Contains| CanvasFile
    end
    
    Identify -->|Reads| Article
    Structure -->|Creates| BreakdownFolder
    Analyze -->|Processes| Article
    Files -->|Creates| SummaryFile
    Files -->|Creates| SectionFiles
    Files -->|Creates| SubsectionFiles
    Canvas -->|Creates| CanvasFile
```

## Workflow Description

The Obsidian Article Breakdown Agent follows a systematic workflow to create structured breakdowns of articles:

1. **Identify Article**: The agent identifies the article in the Obsidian vault based on the path provided by the user.

2. **Create Structure**: The agent creates a new folder in the Obsidian vault to contain the breakdown files.

3. **Analyze Content**: The agent analyzes the article content to identify sections, subsections, and special content.

4. **Create Files**: The agent creates markdown files for the summary, sections, subsections, and special content.

5. **Build Canvas**: The agent creates a canvas file with a visual representation of the article structure.

## Component Interactions

```mermaid
sequenceDiagram
    participant User
    participant Agent as Obsidian Article Breakdown Agent
    participant MCP as Obsidian MCP Server
    participant Vault as Obsidian Vault
    participant LLM as Language Model
    
    User->>Agent: Send message with "Obsidian Mode"
    Agent->>Agent: Extract article path
    
    Agent->>MCP: read_file(article_path)
    MCP->>Vault: Read article content
    Vault-->>MCP: Return article content
    MCP-->>Agent: Return article content
    
    Agent->>Agent: Extract article title
    
    Agent->>MCP: create_folder(breakdown_folder)
    MCP->>Vault: Create breakdown folder
    Vault-->>MCP: Folder created
    MCP-->>Agent: Success
    
    Agent->>LLM: Analyze article content
    LLM-->>Agent: Analysis results
    
    loop For each section and subsection
        Agent->>MCP: write_file(file_path, content)
        MCP->>Vault: Write file
        Vault-->>MCP: File written
        MCP-->>Agent: Success
    end
    
    Agent->>Agent: Generate canvas data
    Agent->>MCP: write_file(canvas_path, canvas_data)
    MCP->>Vault: Write canvas file
    Vault-->>MCP: Canvas file written
    MCP-->>Agent: Success
    
    Agent-->>User: Return success message
```

## File Structure

The agent creates the following file structure in the Obsidian vault:

```
[ArticleTitle]-Breakdown/
├── 00-Summary.md
├── 01-[MainSection].md
├── 01.01-[Subsection].md
├── 01.02-[Subsection].md
├── 02-[MainSection].md
├── ...
├── Key-Concepts.md (optional)
├── References.md (optional)
└── [ArticleTitle]-Breakdown.canvas
```

## Canvas Visualization

The canvas file creates a visual representation of the article structure with the following layout:

```mermaid
graph TD
    Original[Original Article] -->|Link| Summary[Summary]
    Summary -->|Link| Section1[Section 1]
    Summary -->|Link| Section2[Section 2]
    Summary -->|Link| Section3[Section 3]
    Section1 -->|Link| Subsection1_1[Subsection 1.1]
    Section1 -->|Link| Subsection1_2[Subsection 1.2]
    Section2 -->|Link| Subsection2_1[Subsection 2.1]
    Summary -->|Link| SpecialNode[Special Node]
    
    classDef original fill:#9370DB,color:white;
    classDef summary fill:#4CAF50,color:white;
    classDef section fill:#FFEB3B,color:black;
    classDef subsection fill:#00BCD4,color:white;
    classDef special fill:#FF9800,color:white;
    
    class Original original;
    class Summary summary;
    class Section1,Section2,Section3 section;
    class Subsection1_1,Subsection1_2,Subsection2_1 subsection;
    class SpecialNode special;
```

The canvas uses color coding to distinguish different types of nodes:
- Original article: Purple
- Summary: Green
- Level 1 nodes (main sections): Yellow
- Level 2 nodes (subsections): Cyan
- Level 3 nodes (sub-subsections): Blue
- Special nodes: Orange
