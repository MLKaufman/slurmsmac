# SlurmSMAc - Slurm Monitoring Application

A Terminal User Interface (TUI) application for monitoring Slurm jobs, built with Python using Rich and Textual.

## Features

- Real-time monitoring of active and pending Slurm jobs
- Job statistics dashboard with CPU and memory usage
- Historical job data with detailed statistics
- Visual representation of job status distribution
- Auto-refreshing dashboard (every 30 seconds by default)

## Requirements

- Python 3.13 or higher
- Slurm workload manager
- Access to `squeue` and `sacct` commands
- [uv](https://docs.astral.sh/uv/) - A fast Python package installer and resolver

## Installation

1. Install uv (if not already installed):
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/slurmsmac.git
cd slurmsmac
```

3. Install dependencies:
```bash
uv sync
```

This will automatically create a virtual environment and install all dependencies from the lockfile.

## Usage

Run the application:
```bash
uv run python main.py
```

Or activate the virtual environment and run directly:
```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

python main.py
```

The dashboard will show:
- Active jobs table
- Job statistics
- Job history
- Job status distribution plot

The dashboard automatically refreshes every 30 seconds. You can modify the refresh interval by changing the `refresh_interval` value in `main.py`.

## Keyboard Controls

- `q` or `Ctrl+C`: Quit the application
- Arrow keys: Navigate through tables
- Enter: Select a row in tables

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
