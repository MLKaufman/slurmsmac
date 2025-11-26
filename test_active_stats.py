#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test active job stats"""

from src.slurmsmac.slurm_data import MockSlurmDataCollector

def test_active_stats():
    """Test that active jobs have used_memory field."""
    print("Testing active job stats...")

    collector = MockSlurmDataCollector()
    active_jobs = collector.get_active_jobs()
    
    print(f"\nActive jobs columns: {list(active_jobs.columns)}")
    
    if 'used_memory' not in active_jobs.columns:
        print("  ✗ Missing 'used_memory' column")
        return False
    
    print("  ✓ 'used_memory' column present")
        
    # Check data content for running jobs
    running_jobs = active_jobs[active_jobs['state'] == 'RUNNING']
    if not running_jobs.empty:
        job = running_jobs.iloc[0]
        print(f"\nSample Running Job:")
        print(f"  ID: {job['job_id']}")
        print(f"  State: {job['state']}")
        print(f"  Req Mem: {job['memory']}")
        print(f"  Used Mem: {job['used_memory']}")
        
        if job['used_memory'] == 'N/A':
             print("  ✗ Used memory is N/A for running job (unexpected for mock)")
             return False
    else:
        print("\nNo running jobs generated in this mock batch.")
        
    return True

if __name__ == "__main__":
    if test_active_stats():
        print("\n✓ Active stats test passed!")
    else:
        print("\n✗ Active stats test FAILED!")
