from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.reactive import reactive
from textual import events
import matplotlib.pyplot as plt
import io
from datetime import datetime
from .slurm_data import get_slurm_collector, MockSlurmDataCollector
import pandas as pd

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
        /* font-size: 1.2; */
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
        yield Container(
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
            Horizontal(
                Vertical(
                    Static("Job History", classes="section-title"),
                    DataTable(id="history-table"),
                    classes="stats-container"
                ),
                Vertical(
                    Static("Job Status Distribution", classes="section-title"),
                    Static(id="status-plot", classes="plot-container"),
                    classes="stats-container"
                ),
            ),
        )
        if self.is_mock_mode:
            yield Static("⚠️ Running in mock mode - No Slurm detected", classes="mode-indicator")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application when it starts."""
        self.set_interval(self.refresh_interval, self.refresh_data)
        self.refresh_data()

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
        """Update the job status distribution plot."""
        history = self.data_collector.get_job_history()
        status_counts = history['state'].value_counts()
        
        plt.figure(figsize=(6, 4))
        plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')
        plt.title("Job Status Distribution")
        
        # Convert plot to text representation
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Update the plot display
        self.query_one("#status-plot").update("Job Status Distribution Plot")

if __name__ == "__main__":
    app = Dashboard()
    app.run()
