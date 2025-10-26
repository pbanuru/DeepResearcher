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
uv run deep_research.py --input-file example_query.md
```

### Manual input mode
```bash
# Edit manual_input.md with your query, then run:
uv run deep_research.py -m --max-tool-calls 1000
```

### All options
```bash
uv run deep_research.py --help
```

```
usage: deep_research.py [-h]
                        [--model {o3-deep-research,o4-mini-deep-research}]
                        [--no-background] [--max-tool-calls MAX_TOOL_CALLS]
                        [--no-web-search] [--code-interpreter] [--interactive]
                        [--input-file INPUT_FILE] [-m]
                        [--output-dir OUTPUT_DIR] [--no-save]
                        [query]

Conduct deep research using OpenAI's deep research models

positional arguments:
  query                 Research query to investigate

options:
  -h, --help            show this help message and exit
  --model {o3-deep-research,o4-mini-deep-research}
                        Model to use for research (default: o4-mini-deep-
                        research)
  --no-background       Run research synchronously (default: background mode)
  --max-tool-calls MAX_TOOL_CALLS
                        Maximum number of tool calls to make (default: 100)
  --no-web-search       Disable web search
  --code-interpreter    Enable code interpreter for data analysis
  --interactive         Enter interactive mode for multi-line queries
  --input-file INPUT_FILE
                        Read query from a markdown file
  -m, --manual          Read query from manual_input.md
  --output-dir OUTPUT_DIR
                        Directory to save research sessions (default:
                        ./research_sessions)
  --no-save             Don't save research session to disk
```

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
- **Two files per session**:
  - `{folder_name}_research.md` - Combined input query and research output with timestamp
  - `metadata.json` - Session info and tool usage statistics

### Folder Structure Example
```
research_sessions/
├── quantum_computing_developments/
│   ├── quantum_computing_developments_research.md
│   └── metadata.json
├── quantum_computing_developments_001/
│   ├── quantum_computing_developments_001_research.md
│   └── metadata.json
└── mrna_vaccine_effectiveness/
    ├── mrna_vaccine_effectiveness_research.md
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
- Streaming mode and background mode are always enabled for real-time progress updates and reliability
- Default model is `o4-mini-deep-research` (faster/cheaper, use `--model o3-deep-research` for complex tasks)
- Tool calls are capped at 100 by default to control costs
- Research sessions are saved by default to `./research_sessions` (use `--no-save` to disable)
- The tool will show a summary of web searches and code executions made
- Results include inline citations to sources
