# -*- coding: utf-8 -*-
"""SlurmSMAc - Slurm Monitoring Application."""

import os
import sys
from .main import Dashboard

def main():
    """Run the SlurmSMAc dashboard."""
    # Set terminal encoding and type
    if sys.platform != "win32":  # Only set for non-Windows platforms
        # Reconfigure stdin to handle decoding errors gracefully
        # This is critical for HPC environments where terminals may send non-UTF-8 data
        try:
            sys.stdin.reconfigure(encoding='utf-8', errors='replace')
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError, OSError):
            # If reconfigure fails, we'll still set environment variables
            pass

        # Use xterm-256color which is widely supported but disable problematic features
        os.environ["TERM"] = "xterm-256color"
        # Set locale to UTF-8 to ensure proper text handling
        os.environ["LANG"] = "en_US.UTF-8"
        os.environ["LC_ALL"] = "en_US.UTF-8"
        # Tell Python to use UTF-8 with replacement for invalid bytes
        os.environ["PYTHONIOENCODING"] = "utf-8:replace"

    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main() 