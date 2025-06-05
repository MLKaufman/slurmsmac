# -*- coding: utf-8 -*-
"""SlurmSMAc - Slurm Monitoring Application."""

import os
import sys
from .main import Dashboard

def main():
    """Run the SlurmSMAc dashboard."""
    # Set terminal encoding and type
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
    
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main() 