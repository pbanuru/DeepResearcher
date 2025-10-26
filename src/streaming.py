"""Streaming research with rich UI and progress tracking."""

import time
from datetime import datetime, timedelta
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text


class ResearchTracker:
    """Track research progress and display updates."""

    def __init__(self, max_tool_calls, model):
        self.console = Console()
        self.max_tool_calls = max_tool_calls
        self.model = model
        self.start_time = time.time()
        self.tool_calls = 0
        self.web_searches = 0
        self.code_calls = 0
        self.mcp_calls = 0
        self.file_searches = 0
        self.recent_actions = []
        self.max_recent = 5

    def get_elapsed_time(self):
        """Get elapsed time as formatted string."""
        elapsed = time.time() - self.start_time
        return str(timedelta(seconds=int(elapsed)))

    def get_progress_percent(self):
        """Get completion percentage."""
        if self.max_tool_calls == 0:
            return 0.0
        # Cap at 100% even if tool calls exceed max
        percent = (self.tool_calls / self.max_tool_calls) * 100
        return min(100.0, percent)

    def get_eta(self):
        """Calculate ETA for completion."""
        if self.tool_calls == 0:
            return "Calculating...", "Calculating..."

        elapsed = time.time() - self.start_time
        rate = self.tool_calls / elapsed  # tool calls per second
        remaining_calls = self.max_tool_calls - self.tool_calls

        if remaining_calls <= 0 or rate == 0:
            return "0 min", datetime.now().strftime("%H:%M:%S")

        remaining_seconds = remaining_calls / rate
        eta_time = datetime.now() + timedelta(seconds=remaining_seconds)

        # Format remaining time
        remaining_minutes = int(remaining_seconds / 60)
        if remaining_minutes == 0:
            remaining_str = "< 1 min"
        else:
            remaining_str = f"{remaining_minutes} min"

        return remaining_str, eta_time.strftime("%I:%M:%S %p")

    def add_action(self, action_type, description):
        """Add a recent action to the tracker."""
        self.recent_actions.append({
            "type": action_type,
            "desc": description,
            "time": datetime.now().strftime("%I:%M:%S %p")
        })
        if len(self.recent_actions) > self.max_recent:
            self.recent_actions.pop(0)

    def increment_tool_call(self, call_type):
        """Increment tool call counters."""
        self.tool_calls += 1
        if call_type == "web_search_call":
            self.web_searches += 1
        elif call_type == "code_interpreter_call":
            self.code_calls += 1
        elif call_type == "mcp_tool_call":
            self.mcp_calls += 1
        elif call_type == "file_search_call":
            self.file_searches += 1

    def create_display(self):
        """Create the rich display panel."""
        # Progress bar
        progress_percent = self.get_progress_percent()
        remaining_time, eta_time = self.get_eta()

        # Stats table
        stats = Table.grid(padding=(0, 2))
        stats.add_column(style="cyan", justify="right")
        stats.add_column(style="white")

        stats.add_row("Model:", self.model)
        stats.add_row("Elapsed:", self.get_elapsed_time())
        stats.add_row("Progress:", f"{progress_percent:.1f}% ({self.tool_calls}/{self.max_tool_calls} calls)")
        stats.add_row("ETC:", f"{remaining_time} (finishes ~{eta_time})")
        stats.add_row("", "")
        stats.add_row("Web Searches:", str(self.web_searches))
        if self.code_calls > 0:
            stats.add_row("Code Calls:", str(self.code_calls))
        if self.mcp_calls > 0:
            stats.add_row("MCP Calls:", str(self.mcp_calls))
        if self.file_searches > 0:
            stats.add_row("File Searches:", str(self.file_searches))

        # Recent actions
        if self.recent_actions:
            stats.add_row("", "")
            stats.add_row("Recent Actions:", "")
            for action in self.recent_actions[-5:]:
                action_text = Text()
                action_text.append(f"[{action['time']}] ", style="dim")
                action_text.append(action['desc'], style="yellow")
                stats.add_row("", action_text)

        # Progress bar
        bar_width = 40
        filled = int((progress_percent / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        progress_bar = Text()
        progress_bar.append(bar, style="cyan")
        progress_bar.append(f" {progress_percent:.1f}%")

        # Group the table and progress bar
        content = Group(stats, Text(""), progress_bar)

        return Panel(
            content,
            title="[bold green]Deep Research Progress[/bold green]",
            border_style="green"
        )


def stream_research(client, request_params, tracker):
    """Stream research with live progress updates."""
    console = Console()

    # When using background=True with stream=True, we need to get the response object first
    # then iterate over the stream. The response object contains the response_id.
    stream = client.responses.create(**request_params, stream=True)

    # For background streams, the stream itself has metadata we can access
    response_id = None
    events = []
    final_response = None

    try:
        import threading
        stop_updating = threading.Event()

        def periodic_update():
            """Update display periodically even when no events arrive."""
            while not stop_updating.is_set():
                time.sleep(1.0)  # Update once per second
                try:
                    live.update(tracker.create_display())
                except:
                    break

        with Live(tracker.create_display(), console=console, refresh_per_second=2) as live:
            # Start background thread for periodic updates
            update_thread = threading.Thread(target=periodic_update, daemon=True)
            update_thread.start()

            for event in stream:
                events.append(event)

                # Capture response_id from response.created event
                if not response_id:
                    event_type = getattr(event, 'type', None)
                    if event_type == 'response.created':
                        # The response.created event contains the response object with the ID
                        resp = getattr(event, 'response', None)
                        if resp:
                            response_id = getattr(resp, 'id', None)
                            if response_id:
                                console.print(f"[dim]✓ Captured response_id: {response_id}[/dim]")

                        # Also try getting it directly from the event
                        if not response_id:
                            response_id = getattr(event, 'id', None)
                            if response_id and response_id.startswith('resp_'):
                                console.print(f"[dim]✓ Captured response_id from event: {response_id}[/dim]")

                # Handle different event types
                event_type = getattr(event, 'type', None)

                if event_type == 'response.created':
                    tracker.add_action("system", "Research started")

                elif event_type == 'response.output_item.added':
                    item = getattr(event, 'item', None)
                    if item:
                        item_type = getattr(item, 'type', None)
                        if item_type in ['web_search_call', 'code_interpreter_call', 'mcp_tool_call', 'file_search_call']:
                            tracker.increment_tool_call(item_type)

                elif event_type == 'response.done':
                    final_response = getattr(event, 'response', None)
                    tracker.add_action("system", "Research complete!")
                    if final_response:
                        console.print(f"\n[dim]✓ Got final response from stream (status: {getattr(final_response, 'status', 'unknown')})[/dim]")

            # Stop the update thread
            stop_updating.set()

            # Stream ended
            console.print(f"\n[dim]Stream ended. Total events: {len(events)}, Final response: {final_response is not None}[/dim]")

    except KeyboardInterrupt:
        # User pressed Ctrl+C - cancel the background response
        console.print("\n[yellow]Cancelling research...[/yellow]")
        if response_id:
            try:
                cancelled_response = client.responses.cancel(response_id)
                console.print(f"[green]Research cancelled successfully (status: {cancelled_response.status})[/green]")
                return cancelled_response, events
            except Exception as e:
                console.print(f"[red]Error cancelling research: {e}[/red]")
        raise

    # If we didn't get the final response from the stream, fetch it
    if not final_response and response_id:
        console.print(f"\n[yellow]Retrieving final response (ID: {response_id})...[/yellow]")
        try:
            final_response = client.responses.retrieve(response_id)
            console.print(f"[green]✓ Retrieved response (status: {final_response.status})[/green]")
        except Exception as e:
            console.print(f"[red]Error retrieving final response: {e}[/red]")
    elif not response_id:
        console.print(f"\n[red]Error: No response ID captured from stream[/red]")

    return final_response, events
