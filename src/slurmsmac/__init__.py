# -*- coding: utf-8 -*-
"""SlurmSMAc - Slurm Monitoring Application."""

import os
import sys
from .main import Dashboard

def main():
    """Run the SlurmSMAc dashboard."""
    # Set terminal encoding and type
    if sys.platform != "win32":  # Only set for non-Windows platforms
        os.environ["LANG"] = "en_US.UTF-8"
        os.environ["LC_ALL"] = "en_US.UTF-8"
        os.environ["TERM"] = "vt100"  # Use a simple terminal type that doesn't support mouse events
        os.environ["TERMINFO"] = ""
        # Set Python IO encoding
        os.environ["PYTHONIOENCODING"] = "latin-1"
    
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main() 