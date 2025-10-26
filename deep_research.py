#!/usr/bin/env python3
"""
Deep Research CLI Tool
Uses OpenAI's deep research models to conduct comprehensive research on user queries.
"""

import argparse
import os
import sys
from openai import OpenAI
from rich.console import Console

from src.utils import generate_folder_name, create_research_folder
from src.catalog import save_research_session
from src.streaming import ResearchTracker, stream_research


def main():
    parser = argparse.ArgumentParser(
        description="Conduct deep research using OpenAI's deep research models"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Research query to investigate"
    )
    parser.add_argument(
        "--model",
        default="o4-mini-deep-research",
        choices=["o3-deep-research", "o4-mini-deep-research"],
        help="Model to use for research (default: o4-mini-deep-research)"
    )
    parser.add_argument(
        "--no-background",
        action="store_true",
        help="Run research synchronously (default: background mode)"
    )
    parser.add_argument(
        "--max-tool-calls",
        type=int,
        default=100,
        help="Maximum number of tool calls to make (default: 100)"
    )
    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search"
    )
    parser.add_argument(
        "--code-interpreter",
        action="store_true",
        help="Enable code interpreter for data analysis"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enter interactive mode for multi-line queries"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Read query from a markdown file"
    )
    parser.add_argument(
        "-m", "--manual",
        action="store_true",
        help="Read query from manual_input.md"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./research_sessions",
        help="Directory to save research sessions (default: ./research_sessions)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save research session to disk"
    )

    args = parser.parse_args()

    console = Console()

    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        sys.exit(1)

    # Get query from various sources
    query = None
    query_source = "cli"

    if args.manual:
        # Read from manual_input.md
        try:
            with open("manual_input.md", "r") as f:
                query = f.read().strip()
            query_source = "file:manual_input.md"
            console.print(f"[green]✓[/green] Loaded query from manual_input.md")
        except Exception as e:
            console.print(f"[red]Error reading manual_input.md: {e}[/red]")
            sys.exit(1)
    elif args.input_file:
        # Read from markdown file
        try:
            with open(args.input_file, "r") as f:
                query = f.read().strip()
            query_source = f"file:{args.input_file}"
            console.print(f"[green]✓[/green] Loaded query from {args.input_file}")
        except Exception as e:
            console.print(f"[red]Error reading input file: {e}[/red]")
            sys.exit(1)
    elif args.interactive:
        # Interactive mode
        console.print("[cyan]Enter your research query (press Ctrl+D when done):[/cyan]")
        query = sys.stdin.read().strip()
        query_source = "interactive"
    elif args.query:
        # Command line argument
        query = args.query
        query_source = "cli"
    else:
        # No query provided
        console.print("[red]Error: No query provided. Use a query argument, --input-file, or --interactive[/red]")
        sys.exit(1)

    if not query:
        console.print("[red]Error: Query is empty[/red]")
        sys.exit(1)

    # Initialize client
    client = OpenAI(api_key=api_key, timeout=3600)

    # Generate folder structure if saving
    research_folder = None
    if not args.no_save:
        console.print("[cyan]Generating folder name...[/cyan]")
        folder_name = generate_folder_name(client, query)
        research_folder = create_research_folder(args.output_dir, folder_name)
        console.print(f"[green]✓[/green] Research will be saved to: [bold]{research_folder}[/bold]")

    # Build tools list
    tools = []
    if not args.no_web_search:
        tools.append({"type": "web_search_preview"})
    if args.code_interpreter:
        tools.append({"type": "code_interpreter", "container": {"type": "auto"}})

    if not tools:
        console.print("[red]Error: At least one tool must be enabled[/red]")
        sys.exit(1)

    # Build request parameters - always use background and streaming for better UX
    request_params = {
        "model": args.model,
        "input": query,
        "background": True,  # Always use background mode with streaming
        "tools": tools,
        "max_tool_calls": args.max_tool_calls,
    }

    console.print(f"\n[bold cyan]Starting research with {args.model}[/bold cyan]")
    console.print(f"[dim]Query: {query[:100]}{'...' if len(query) > 100 else ''}[/dim]\n")

    # Create research request with streaming
    try:
        tracker = ResearchTracker(args.max_tool_calls, args.model)
        response, _ = stream_research(client, request_params, tracker)

        # Output results
        if response and response.status == "completed":
            console.print("\n[bold green]" + "=" * 80 + "[/bold green]")
            console.print("[bold green]RESEARCH RESULTS[/bold green]")
            console.print("[bold green]" + "=" * 80 + "[/bold green]\n")
            console.print(response.output_text)
            console.print()

            # Show tool usage summary
            if hasattr(response, 'output') and response.output:
                web_searches = sum(1 for item in response.output if getattr(item, 'type', None) == 'web_search_call')
                code_calls = sum(1 for item in response.output if getattr(item, 'type', None) == 'code_interpreter_call')

                console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
                console.print("[bold cyan]TOOL USAGE SUMMARY[/bold cyan]")
                console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
                if web_searches:
                    console.print(f"[green]Web searches:[/green] {web_searches}")
                if code_calls:
                    console.print(f"[green]Code interpreter calls:[/green] {code_calls}")

            # Save research session
            if research_folder:
                console.print()
                console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
                console.print("[bold cyan]SAVING RESEARCH SESSION[/bold cyan]")
                console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
                combined_file, metadata_file = save_research_session(
                    research_folder, query, response, args, query_source
                )
                console.print(f"[green]Research saved to:[/green]  {combined_file}")
                console.print(f"[green]Metadata saved to:[/green] {metadata_file}")
        elif response and response.status == "cancelled":
            console.print(f"\n[yellow]Research was cancelled. Partial results may not be available.[/yellow]")
            sys.exit(0)
        else:
            status = response.status if response else "unknown"
            console.print(f"[red]Error: Research failed with status: {status}[/red]")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
