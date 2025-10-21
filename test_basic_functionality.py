#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic functionality test for SlurmSMAc"""

from src.slurmsmac.slurm_data import get_slurm_collector, MockSlurmDataCollector
import pandas as pd

def test_data_collector():
    """Test the data collector functionality."""
    print("Testing Slurm Data Collector...")

    # Get the appropriate collector
    collector = get_slurm_collector()

    # Check if we're in mock mode
    is_mock = isinstance(collector, MockSlurmDataCollector)
    print(f"  Mode: {'Mock' if is_mock else 'Real Slurm'}")

    # Test get_active_jobs
    print("\n1. Testing get_active_jobs()...")
    active_jobs = collector.get_active_jobs()
    print(f"  Type: {type(active_jobs)}")
    print(f"  Number of active jobs: {len(active_jobs)}")
    if not active_jobs.empty:
        print(f"  Columns: {list(active_jobs.columns)}")
        print(f"  First job:\n{active_jobs.iloc[0].to_dict()}")
    else:
        print("  No active jobs found")

    # Test get_job_history
    print("\n2. Testing get_job_history()...")
    history = collector.get_job_history()
    print(f"  Type: {type(history)}")
    print(f"  Number of historical jobs: {len(history)}")
    if not history.empty:
        print(f"  Columns: {list(history.columns)}")
        print(f"  States: {history['state'].unique()}")
    else:
        print("  No job history found")

    # Test get_job_stats
    print("\n3. Testing get_job_stats()...")
    stats = collector.get_job_stats()
    print(f"  Type: {type(stats)}")
    print(f"  Stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.2f}")
        else:
            print(f"    {key}: {value}")

    print("\n✓ All basic functionality tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_data_collector()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
