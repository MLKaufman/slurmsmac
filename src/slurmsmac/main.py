# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Tab, Tabs, TabPane
from .slurm_data import get_slurm_collector, MockSlurmDataCollector

# Note: Mouse support is disabled in this application to ensure compatibility
# with HPC environments. The previous driver patch for handling non-UTF-8 mouse
# sequences has been removed as it was interfering with keyboard input.

class Dashboard(App):
    """Main dashboard application."""

    # Disable mouse support completely - MUST be class attributes set before __init__
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("tab", "switch_tab", "Switch Tab"),
        ("up", "cursor_up", "Up"),
        ("down", "cursor_down", "Down"),
    ]

    CSS = """
    Screen {
        background: red;
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

    DataTable {
        height: 1fr;
        border: solid $primary;
    }

    DataTable:focus {
        border: solid $success;
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
    """

    def __init__(self):
        # Disable mouse BEFORE calling super().__init__() to prevent driver from enabling it
        # These must be set on the class before Textual initializes the driver
        Dashboard.ENABLE_COMMAND_PALETTE = False

        super().__init__()

        # Disable mouse support at multiple levels for HPC compatibility
        self.mouse_over = None
        try:
            self._mouse_down_widget = None
        except:
            pass

        self.data_collector = get_slurm_collector()
        self.refresh_interval = 30  # seconds
        self.is_mock_mode = isinstance(self.data_collector, MockSlurmDataCollector)
        # Track current tab
        self.current_tab_index = 0
        self.tab_ids = ["current-tab", "history-tab"]

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
                Vertical(
                    Static("Active Jobs", classes="section-title"),
                    DataTable(id="active-jobs-table"),
                    classes="stats-container"
                ),
            ),
            id="current-pane"
        )
        yield TabPane(
            "Job History",
            Container(
                Vertical(
                    Static("Job History", classes="section-title"),
                    DataTable(id="history-table"),
                    classes="stats-container"
                ),
            ),
            id="history-pane"
        )
        if self.is_mock_mode:
            yield Static("⚠️ Running in mock mode - No Slurm detected", classes="mode-indicator")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application when it starts."""
        # Disable mouse support at the application level
        # This prevents issues with HPC terminals that may send mouse events
        try:
            self.mouse_mode = "none"
            self.mouse_support = False
        except (AttributeError, ValueError):
            # If mouse configuration fails, continue anyway
            pass

        self.set_interval(self.refresh_interval, self.refresh_data)
        self.refresh_data()

        # Focus the active jobs table initially
        try:
            active_table = self.query_one("#active-jobs-table")
            active_table.focus()
        except:
            pass

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_switch_tab(self) -> None:
        """Switch to the next tab."""
        # Toggle between the two tabs
        self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_ids)

        try:
            tabs_widget = self.query_one(Tabs)
            tabs_widget.active = self.tab_ids[self.current_tab_index]

            # Focus the appropriate table based on the current tab
            if self.current_tab_index == 0:
                table = self.query_one("#active-jobs-table")
            else:
                table = self.query_one("#history-table")
            table.focus()
        except:
            pass

    def action_cursor_up(self) -> None:
        """Move cursor up in the current table."""
        try:
            focused = self.focused
            if isinstance(focused, DataTable):
                focused.action_cursor_up()
        except:
            pass

    def action_cursor_down(self) -> None:
        """Move cursor down in the current table."""
        try:
            focused = self.focused
            if isinstance(focused, DataTable):
                focused.action_cursor_down()
        except:
            pass

    def on_key(self, event):
        """Handle keyboard events."""
        if event.key == "ctrl+c":
            self.exit()

    def refresh_data(self) -> None:
        """Refresh all data displays."""
        self.update_active_jobs()
        self.update_job_history()

    def update_active_jobs(self) -> None:
        """Update the active jobs table."""
        table = self.query_one("#active-jobs-table")
        table.clear(columns=True)
        table.add_columns("Job ID", "Name", "State", "Time", "CPUs", "Memory")
        table.cursor_type = "row"
        table.can_focus = True

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

    def update_job_history(self) -> None:
        """Update the job history table."""
        table = self.query_one("#history-table")
        table.clear(columns=True)
        table.add_columns("Job ID", "Name", "State", "Start", "End", "Elapsed", "CPUs", "Memory")
        table.cursor_type = "row"
        table.can_focus = True

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

if __name__ == "__main__":
    app = Dashboard()
    app.run()
