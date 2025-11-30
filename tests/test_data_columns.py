#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test data column compatibility"""

from slurmsmac.slurm_data import MockSlurmDataCollector

def test_column_compatibility():
    """Test that mock data has all required columns."""
    print("Testing data column compatibility...")

    collector = MockSlurmDataCollector()

    # Test active jobs columns
    print("\n1. Active jobs columns:")
    active_jobs = collector.get_active_jobs()
    print(f"  Columns: {list(active_jobs.columns)}")
    required_active_cols = ['job_id', 'name', 'state', 'time', 'cpus', 'memory']
    missing = [col for col in required_active_cols if col not in active_jobs.columns]
    if missing:
        print(f"  ✗ Missing columns: {missing}")
    else:
        print(f"  ✓ All required columns present")

    # Test job history columns
    print("\n2. Job history columns:")
    history = collector.get_job_history()
    print(f"  Columns: {list(history.columns)}")
    required_history_cols = ['job_id', 'name', 'state', 'start', 'end', 'elapsed', 'ncpus', 'max_rss']
    missing = [col for col in required_history_cols if col not in history.columns]
    if missing:
        print(f"  ✗ Missing columns: {missing}")
        return False
    else:
        print(f"  ✓ All required columns present")

    print("\n3. Testing data access:")
    if not history.empty:
        try:
            job = history.iloc[0]
            print(f"  job_id: {job['job_id']}")
            print(f"  name: {job['name']}")
            print(f"  state: {job['state']}")
            print(f"  start: {job['start']}")
            print(f"  end: {job['end']}")
            print(f"  elapsed: {job['elapsed']}")
            print(f"  ncpus: {job['ncpus']}")
            print(f"  max_rss: {job['max_rss']}")
            print(f"  ✓ Can access all required fields")
        except KeyError as e:
            print(f"  ✗ Cannot access field: {e}")
            return False

    return True

if __name__ == "__main__":
    try:
        if test_column_compatibility():
            print("\n✓ Column compatibility test passed!")
        else:
            print("\n✗ Column compatibility test FAILED!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
