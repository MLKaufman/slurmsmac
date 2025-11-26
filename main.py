#!/usr/bin/env python3
"""
SlurmSMAc - Slurm Monitoring Application
This is a wrapper script to run the application from the root directory.
"""
import sys
import os

# Add the src directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from slurmsmac.main import Dashboard

if __name__ == "__main__":
    app = Dashboard()
    app.run()
