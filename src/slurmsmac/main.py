# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Label, Tab, Tabs, TabPane
from textual.reactive import reactive
from datetime import datetime
from .slurm_data import get_slurm_collector, MockSlurmDataCollector
import pandas as pd
import os
import sys

class JobStats(Static):
    """Widget to display job statistics."""
    def __init__(self, title: str, value: str):
        super().__init__()
        self.title = title
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(self.title, classes="stats-title")
        yield Label(self.value, classes="stats-value")

class Dashboard(App):
    """Main dashboard application."""
    CSS = """
    Screen {
        background: $surface;
    }

    #header {
        background: $accent;
        color: $text;
        height: 3;
    }

    #footer {
        background: $accent;
        color: $text;
        height: 3;
    }

    .stats-container {
        height: 1fr;
        width: 1fr;
        padding: 1;
    }

    .stats-title {
        color: $text-muted;
    }

    .stats-value {
        color: $text;
    }

    DataTable {
        height: 1fr;
        border: solid $primary;
    }

    .plot-container {
        height: 1fr;
        width: 1fr;
        padding: 1;
    }

    .mode-indicator {
        color: $warning;
        text-style: bold;
    }

    Tabs {
        dock: top;
        width: 100%;
        height: 3;
    }

    TabPane {
        height: 1fr;
    }

    .status-bar {
        color: $text;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.data_collector = get_slurm_collector()
        self.refresh_interval = 30  # seconds
        self.is_mock_mode = isinstance(self.data_collector, MockSlurmDataCollector)
        # Store JobStats widgets for direct access
        self.total_jobs_stat = JobStats("Total Jobs", "0")
        self.active_jobs_stat = JobStats("Active Jobs", "0")
        self.completed_jobs_stat = JobStats("Completed Jobs", "0")
        self.failed_jobs_stat = JobStats("Failed Jobs", "0")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Tabs(
            Tab("Current Jobs", id="current-tab"),
            Tab("Job History", id="history-tab"),
        )
        yield TabPane(
            "Current Jobs",
            Container(
                Horizontal(
                    Vertical(
                        Static("Active Jobs", classes="section-title"),
                        DataTable(id="active-jobs-table"),
                        classes="stats-container"
                    ),
                    Vertical(
                        Static("Job Statistics", classes="section-title"),
                        self.total_jobs_stat,
                        self.active_jobs_stat,
                        self.completed_jobs_stat,
                        self.failed_jobs_stat,
                        classes="stats-container"
                    ),
                ),
            ),
            id="current-pane"
        )
        yield TabPane(
            "Job History",
            Container(
                Horizontal(
                    Vertical(
                        Static("Job History", classes="section-title"),
                        DataTable(id="history-table"),
                        classes="stats-container"
                    ),
                    Vertical(
                        Static("Job Status Distribution", classes="section-title"),
                        Static(id="status-plot", classes="status-bar"),
                        classes="stats-container"
                    ),
                ),
            ),
            id="history-pane"
        )
        if self.is_mock_mode:
            yield Static("⚠️ Running in mock mode - No Slurm detected", classes="mode-indicator")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application when it starts."""
        # Set terminal encoding for the application
        if sys.platform != "win32":  # Only set for non-Windows platforms
            # Use dumb terminal type which has no special features
            os.environ["TERM"] = "dumb"
            os.environ["TERMINFO"] = ""
            # Disable all mouse tracking
            os.environ["MOUSE_TRACKING"] = "0"
            os.environ["TERM_PROGRAM"] = "dumb"
            # Set encoding to latin-1 which is more permissive
            os.environ["LANG"] = "C"
            os.environ["LC_ALL"] = "C"
            os.environ["PYTHONIOENCODING"] = "latin-1"
            # Disable any terminal features that might enable mouse
            os.environ["TERM_PROGRAM_VERSION"] = "0"
            os.environ["TERM_SESSION_ID"] = "0"
            os.environ["TERM_SESSION_NAME"] = "dumb"
        
        # Completely disable mouse support at the application level
        self.mouse_mode = "none"
        self.mouse_support = False
        
        self.set_interval(self.refresh_interval, self.refresh_data)
        self.refresh_data()

    def on_key(self, event):
        """Handle keyboard events."""
        if event.key == "q":
            self.exit()
        elif event.key == "ctrl+c":
            self.exit()

    def refresh_data(self) -> None:
        """Refresh all data displays."""
        self.update_active_jobs()
        self.update_job_stats()
        self.update_job_history()
        self.update_status_plot()

    def update_active_jobs(self) -> None:
        """Update the active jobs table."""
        table = self.query_one("#active-jobs-table")
        table.clear()
        table.add_columns("Job ID", "Name", "State", "Time", "CPUs", "Memory")
        
        active_jobs = self.data_collector.get_active_jobs()
        for _, job in active_jobs.iterrows():
            table.add_row(
                job['job_id'],
                job['name'],
                job['state'],
                job['time'],
                job['cpus'],
                job['memory']
            )

    def update_job_stats(self) -> None:
        """Update the job statistics display."""
        stats = self.data_collector.get_job_stats()
        self.total_jobs_stat.value = str(stats.get('total_jobs', 0))
        self.active_jobs_stat.value = str(stats.get('active_jobs', 0))
        self.completed_jobs_stat.value = str(stats.get('completed_jobs', 0))
        self.failed_jobs_stat.value = str(stats.get('failed_jobs', 0))

    def update_job_history(self) -> None:
        """Update the job history table."""
        table = self.query_one("#history-table")
        table.clear()
        table.add_columns("Job ID", "Name", "State", "Start", "End", "Elapsed", "CPUs", "Memory")
        
        history = self.data_collector.get_job_history()
        for _, job in history.iterrows():
            table.add_row(
                job['job_id'],
                job['name'],
                job['state'],
                job['start'],
                job['end'],
                job['elapsed'],
                job['ncpus'],
                job['max_rss']
            )

    def update_status_plot(self) -> None:
        """Update the job status distribution display."""
        try:
            history = self.data_collector.get_job_history()
            if history.empty:
                self.query_one("#status-plot").update("No job history available")
                return

            status_counts = history['state'].value_counts()
            total_jobs = len(history)
            
            # Create a text-based visualization using ASCII characters only
            lines = ["Job Status Distribution:"]
            for status, count in status_counts.items():
                percentage = (count / total_jobs) * 100
                bar_length = int(percentage / 2)  # Scale bar to fit in terminal
                bar = "#" * bar_length  # Use ASCII # instead of Unicode block
                lines.append(f"{status:12} {bar} {percentage:5.1f}% ({count})")
            
            # Add total jobs count
            lines.append(f"\nTotal Jobs: {total_jobs}")
            
            # Update the display
            self.query_one("#status-plot").update("\n".join(lines))
        except Exception as e:
            # If there's any error, show a simple text representation
            self.query_one("#status-plot").update(f"Error generating status display: {str(e)}")

if __name__ == "__main__":
    app = Dashboard()
    app.run()
