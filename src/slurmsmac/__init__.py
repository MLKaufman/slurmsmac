"""SlurmSMAc - Slurm Monitoring Application."""

from .main import Dashboard

def main():
    """Run the SlurmSMAc dashboard."""
    app = Dashboard()
    app.run()

if __name__ == "__main__":
    main()
