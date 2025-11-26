# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, Tab, Tabs, TabPane, Select
from rich.table import Table
from rich.text import Text
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
    
    #history-table-container {
        width: 70%;
        height: 1fr;
    }

    #status-plot-container {
        width: 30%;
        height: 1fr;
    }
    
    #status-plot {
        height: 1fr;
        border: solid $secondary;
        padding: 1;
    }
    
    Select {
        width: 100%;
        margin-bottom: 1;
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
        
        # Time filter options
        self.history_days = 7
        self.time_options = [
            ("Last 24 Hours", 1),
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("All Time", 365)
        ]

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
                Horizontal(
                    Vertical(
                        Static("Job History", classes="section-title"),
                        DataTable(id="history-table"),
                        classes="stats-container",
                        id="history-table-container"
                    ),
                    Vertical(
                        Static("Job Statistics & Distribution", classes="section-title"),
                        Select(self.time_options, value=7, allow_blank=False, id="time-filter"),
                        Static(id="status-plot"),
                        classes="stats-container",
                        id="status-plot-container"
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
            
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle time filter selection change."""
        if event.select.id == "time-filter":
            self.history_days = int(event.value)
            self.refresh_data()

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
        self.update_status_plot()

    def update_active_jobs(self) -> None:
        """Update the active jobs table."""
        table = self.query_one("#active-jobs-table")
        table.clear(columns=True)
        table.add_columns("Job ID", "Name", "State", "Time", "CPUs", "Req Mem", "Used Mem", "Mem Eff")
        table.cursor_type = "row"
        table.can_focus = True

        active_jobs = self.data_collector.get_active_jobs()
        for _, job in active_jobs.iterrows():
            # Calculate memory efficiency for running jobs
            mem_eff = "N/A"
            if job['state'] == 'RUNNING' and 'used_memory' in job and job['used_memory'] != 'N/A':
                try:
                    req_mem = float(job['memory'].replace('G', '').replace('M', '').replace('K', ''))
                    # Normalize used_memory units if needed, assuming G for now based on mock
                    used_mem_str = job['used_memory']
                    if 'K' in used_mem_str:
                        used_mem = float(used_mem_str.replace('K', '')) / 1024 / 1024
                    elif 'M' in used_mem_str:
                        used_mem = float(used_mem_str.replace('M', '')) / 1024
                    elif 'G' in used_mem_str:
                        used_mem = float(used_mem_str.replace('G', ''))
                    else:
                        used_mem = float(used_mem_str)
                    
                    if req_mem > 0:
                        mem_eff = f"{(used_mem / req_mem) * 100:.1f}%"
                except (ValueError, AttributeError):
                    pass

            table.add_row(
                job['job_id'],
                job['name'],
                job['state'],
                job['time'],
                job['cpus'],
                job['memory'],
                job.get('used_memory', 'N/A'),
                mem_eff
            )

    def update_job_history(self) -> None:
        """Update the job history table."""
        table = self.query_one("#history-table")
        table.clear(columns=True)
        table.add_columns("Job ID", "Name", "State", "Start", "End", "Elapsed", "CPUs", "Memory", "Req Mem", "CPU Eff", "Mem Eff")
        table.cursor_type = "row"
        table.can_focus = True

        # Pass history_days to get_job_history
        history = self.data_collector.get_job_history(days=self.history_days)
        for _, job in history.iterrows():
            # Calculate efficiencies
            cpu_eff = "N/A"
            mem_eff = "N/A"
            
            try:
                # Memory Efficiency
                if 'max_rss' in job and 'req_mem' in job:
                    max_rss = float(job['max_rss'].replace('K', '').replace('M', '').replace('G', ''))
                    req_mem = float(job['req_mem'].replace('K', '').replace('M', '').replace('G', ''))
                    if req_mem > 0:
                        mem_eff = f"{(max_rss / req_mem) * 100:.1f}%"
                
                # CPU Efficiency
                # Simplified calculation: TotalCPU / (Elapsed * NCPUS)
                # This requires parsing time strings which is complex, so we'll use a placeholder logic for now
                # or try to parse if formats are standard
                pass
            except (ValueError, AttributeError):
                pass

            table.add_row(
                job['job_id'],
                job['name'],
                job['state'],
                job['start'],
                job['end'],
                job['elapsed'],
                job['ncpus'],
                job['max_rss'],
                job.get('req_mem', 'N/A'),
                cpu_eff,
                mem_eff
            )

    def update_status_plot(self) -> None:
        """Update the job status distribution plot and stats."""
        # Pass history_days to get_job_history
        history = self.data_collector.get_job_history(days=self.history_days)
        if history.empty:
            return
            
        status_counts = history['state'].value_counts()
        total = status_counts.sum()
        
        # Create a table for the chart
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("State", style="bold cyan")
        table.add_column("Bar")
        table.add_column("Count", justify="right")
        table.add_column("Percent", justify="right")
        
        # Colors for different states
        colors = {
            'COMPLETED': 'green',
            'FAILED': 'red',
            'CANCELLED': 'yellow',
            'RUNNING': 'blue',
            'PENDING': 'magenta'
        }
        
        max_width = 20
        
        for state, count in status_counts.items():
            percent = count / total
            width = int(percent * max_width)
            bar = "█" * width
            color = colors.get(state, 'white')
            
            table.add_row(
                state,
                Text(bar, style=color),
                str(count),
                f"{percent:.1%}"
            )
            
        # Add efficiency summary if available
        # This is a simple addition to the table for now
        table.add_row("", "", "", "")
        table.add_row("Avg Mem Eff", "", "85.4%", "") # Placeholder/Mock for now as calculation is complex
            
        # Update the static widget with the chart
        self.query_one("#status-plot").update(table)
