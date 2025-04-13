# Example Files for Obsidian Article Breakdown Agent

This directory contains example files that you can use to test the Obsidian Article Breakdown Agent.

## Sample Files

### Sample Article

The `sample-article.md` file is a comprehensive guide to Markdown that you can use to test the agent. It's a medium-length article with multiple sections and subsections, making it ideal for demonstrating the agent's capabilities.

### Sample Canvas Generator

The `generate_sample_canvas.py` script generates a sample Obsidian canvas file that demonstrates the structure of the canvas files created by the agent. To use it:

```bash
python generate_sample_canvas.py
```

This will create a `sample-canvas.canvas` file in the examples directory that you can copy to your Obsidian vault to see how the canvas visualization looks.

## How to Use the Sample Article

1. Copy the `sample-article.md` file to your Obsidian vault, preferably in a "Clippings" folder.

2. Start the agent and the MCP server using the run script:
   ```bash
   python run_agent.py --vault-path /path/to/your/obsidian/vault
   ```

3. Interact with the agent by sending a message with "Obsidian Mode" and the path to the article:
   ```
   Obsidian Mode
   Please create a breakdown for the article at path: Clippings/sample-article.md
   ```

4. The agent will analyze the article and create a structured breakdown with:
   - A summary file
   - Files for each main section
   - Files for subsections
   - A canvas visualization

5. Open the canvas file in Obsidian to see the visual representation of the article structure.

## Expected Output

After processing the sample article, you should see a new folder in your Obsidian vault named "Understanding Markdown-Breakdown" containing:

- `00-Summary.md`: A summary of the article with links to all sections
- `01-Why-Use-Markdown.md`: The first main section
- `02-Basic-Syntax.md`: The second main section
- `02.01-Headers.md`: A subsection of Basic Syntax
- `02.02-Emphasis.md`: A subsection of Basic Syntax
- `02.03-Lists.md`: A subsection of Basic Syntax
- `02.04-Links.md`: A subsection of Basic Syntax
- `02.05-Images.md`: A subsection of Basic Syntax
- `03-Advanced-Markdown-Features.md`: The third main section
- `04-Markdown-in-Different-Environments.md`: The fourth main section
- `05-Best-Practices.md`: The fifth main section
- `06-Conclusion.md`: The conclusion section
- `References.md`: A special node for references
- `Understanding Markdown-Breakdown.canvas`: The canvas visualization

## Creating Your Own Examples

You can create your own example articles to test the agent with different types of content:

1. Create a markdown file with your content.
2. Make sure it has a clear structure with headings and subheadings.
3. Copy it to your Obsidian vault.
4. Use the agent to create a breakdown as described above.

The agent works best with well-structured articles that have clear sections and subsections.
