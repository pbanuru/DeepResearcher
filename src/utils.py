"""Utility functions for deep research tool."""

import re
from pathlib import Path


def generate_folder_name(client, query):
    """Generate a concise folder name based on the query using GPT."""
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            reasoning={"effort": "low"},
            input=f"Generate a short, descriptive folder name (2-4 words, snake_case) for this research query: '{query}'. Only return the folder name, nothing else.",
        )
        folder_name = response.output_text.strip().lower()
        # Clean up the folder name
        folder_name = re.sub(r'[^\w\s-]', '', folder_name)
        folder_name = re.sub(r'[-\s]+', '_', folder_name)
        return folder_name
    except Exception as e:
        # Fallback to a simple truncated version
        fallback = re.sub(r'[^\w\s-]', '', query.lower())[:40]
        fallback = re.sub(r'[-\s]+', '_', fallback)
        return fallback


def create_research_folder(base_dir, folder_name):
    """Create a unique research folder with disambiguation code if needed."""
    base_path = Path(base_dir) / folder_name

    # If folder doesn't exist, create it
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    # If it exists, add disambiguation code
    counter = 1
    while True:
        disambiguated_path = Path(base_dir) / f"{folder_name}_{counter:03d}"
        if not disambiguated_path.exists():
            disambiguated_path.mkdir(parents=True, exist_ok=True)
            return disambiguated_path
        counter += 1
