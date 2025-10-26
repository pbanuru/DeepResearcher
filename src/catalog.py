"""Research session cataloging functions."""

import json
from datetime import datetime


def save_research_session(folder_path, query, response, args, query_source="cli"):
    """Save the research session data to files."""
    timestamp = datetime.now().isoformat()

    # Get folder name for file prefixes
    folder_name = folder_path.name

    # Save combined input and output in a single document
    combined_file = folder_path / f"{folder_name}_research.md"
    with open(combined_file, "w") as f:
        f.write("# Research Session\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        f.write("---\n\n")
        f.write("## Input Query\n\n")
        f.write(query)
        f.write("\n\n")
        f.write("---\n\n")
        f.write("## Research Output\n\n")
        f.write(response.output_text)
        f.write("\n")

    # Save metadata and tool usage
    metadata = {
        "timestamp": timestamp,
        "query": query,
        "query_source": query_source,
        "model": args.model,
        "response_id": response.id,
        "status": response.status,
        "max_tool_calls": args.max_tool_calls,
        "web_search_enabled": not args.no_web_search,
        "code_interpreter_enabled": args.code_interpreter,
        "background_mode": not args.no_background,
    }

    # Add tool usage statistics
    if hasattr(response, 'output') and response.output:
        web_searches = sum(1 for item in response.output if getattr(item, 'type', None) == 'web_search_call')
        code_calls = sum(1 for item in response.output if getattr(item, 'type', None) == 'code_interpreter_call')
        metadata["tool_usage"] = {
            "web_searches": web_searches,
            "code_interpreter_calls": code_calls,
        }

    metadata_file = folder_path / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    return combined_file, metadata_file
