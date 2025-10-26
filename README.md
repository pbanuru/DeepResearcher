# Deep Researcher

A command-line tool for conducting comprehensive research using OpenAI's deep research models. Features real-time streaming progress, AI-generated folder names, and automatic session cataloging.

## Setup

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. Run the tool with uv:
```bash
uv run deep_research.py "your research query"
```

## Usage

### Basic research query
```bash
uv run deep_research.py "What are the latest developments in quantum computing?"
```

### Read query from markdown file
```bash
uv run deep_research.py --input-file my_query.md
```

### Interactive mode (for multi-line queries)
```bash
uv run deep_research.py --interactive
```

### Synchronous mode (background is default)
```bash
uv run deep_research.py --no-background "Quick research query"
```

### Enable code interpreter for data analysis
```bash
uv run deep_research.py --code-interpreter "Analyze trends in global temperature data"
```

### Use the more powerful model
```bash
uv run deep_research.py --model o3-deep-research "Complex research query"
```

### Adjust tool call limit
```bash
uv run deep_research.py --max-tool-calls 50 "Research topic"
```

### Disable web search (for analysis only)
```bash
uv run deep_research.py --no-web-search --code-interpreter "Analyze this dataset"
```

### Custom output directory
```bash
uv run deep_research.py --output-dir ~/my_research "Research topic"
```

### Don't save to disk
```bash
uv run deep_research.py --no-save "Quick lookup"
```

## Options

### Input Options
- `query` - Research query to investigate (required unless --interactive or --input-file is used)
- `--input-file` - Read query from a markdown file
- `--interactive` - Enter interactive mode for multi-line queries

### Model Options
- `--model` - Model to use: `o4-mini-deep-research` (default) or `o3-deep-research`
- `--no-background` - Run research synchronously instead of background mode (default: background)
- `--max-tool-calls` - Maximum number of tool calls to make (default: 100)

### Tool Options
- `--no-web-search` - Disable web search tool
- `--code-interpreter` - Enable code interpreter for data analysis

### Output Options
- `--output-dir` - Directory to save research sessions (default: ./research_sessions)
- `--no-save` - Don't save research session to disk

## Examples

### Academic research
```bash
uv run deep_research.py "Research the effectiveness of mRNA vaccines. Include peer-reviewed studies, clinical trial data, and regulatory approvals."
```

### Research from markdown file
```bash
uv run deep_research.py --input-file example_query.md
```

The tool includes `example_query.md` showing how to structure complex research queries with multiple sections and requirements.

### Market analysis
```bash
uv run deep_research.py "Analyze the electric vehicle market in 2025. Include market share, sales trends, and major manufacturers."
```

### Data analysis with code
```bash
uv run deep_research.py --code-interpreter "Analyze climate trends and predict future patterns"
```

## Research Session Cataloging

By default, every research session is automatically saved with:
- **Auto-generated folder name** - GPT-5-mini generates a descriptive folder name based on your query
- **Disambiguation codes** - If a folder exists, adds `_001`, `_002`, etc.
- **Three files per session**:
  - `input.md` - Your original query with metadata
  - `output.md` - Research results
  - `metadata.json` - Session info and tool usage statistics

### Folder Structure Example
```
research_sessions/
├── quantum_computing_developments/
│   ├── input.md
│   ├── output.md
│   └── metadata.json
├── quantum_computing_developments_001/
│   ├── input.md
│   ├── output.md
│   └── metadata.json
└── mrna_vaccine_effectiveness/
    ├── input.md
    ├── output.md
    └── metadata.json
```

## Live Progress Tracking

The tool streams research progress in real-time with a rich UI showing:

- **Progress bar** - Visual indication of completion (tool calls used / max tool calls)
- **Elapsed time** - How long the research has been running
- **ETA** - Estimated time remaining and completion time
- **Live statistics** - Real-time counts of web searches, code executions, etc.
- **Recent actions** - Last 5 research actions with timestamps

Example display:
```
┏━━━━━━━━━━━━━ Deep Research Progress ━━━━━━━━━━━━━┓
┃         Model: o4-mini-deep-research              ┃
┃       Elapsed: 0:02:34                            ┃
┃      Progress: 42.0% (42/100 calls)               ┃
┃           ETA: 3 min (finishes ~02:32:15 PM)      ┃
┃                                                    ┃
┃  Web Searches: 38                                 ┃
┃    Code Calls: 4                                  ┃
┃                                                    ┃
┃ Recent Actions:                                   ┃
┃    [02:29:41 PM] Searching: quantum computing    ┃
┃    [02:29:45 PM] Opening: nature.com/article...  ┃
┃    [02:29:50 PM] Executing code                  ┃
┃                                                    ┃
┃ ████████████████████░░░░░░░░░░░░░░░░░░░ 42.0%    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Notes

- Deep research can take several minutes to complete
- Streaming mode is always enabled for real-time progress updates
- Background mode is enabled by default for reliability
- Default model is `o4-mini-deep-research` (faster/cheaper, use `--model o3-deep-research` for complex tasks)
- Tool calls are capped at 100 by default to control costs
- Research sessions are saved by default to `./research_sessions` (use `--no-save` to disable)
- The tool will show a summary of web searches and code executions made
- Results include inline citations to sources
