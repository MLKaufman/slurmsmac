#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test efficiency stats data fields"""

from src.slurmsmac.slurm_data import MockSlurmDataCollector

def test_efficiency_fields():
    """Test that mock data has efficiency-related fields."""
    print("Testing efficiency data fields...")

    collector = MockSlurmDataCollector()
    history = collector.get_job_history()
    
    print(f"\nJob history columns: {list(history.columns)}")
    
    required_cols = ['req_mem', 'total_cpu', 'max_rss', 'ncpus', 'elapsed']
    missing = [col for col in required_cols if col not in history.columns]
    
    if missing:
        print(f"  ✗ Missing columns: {missing}")
        return False
    else:
        print(f"  ✓ All required columns present")
        
    # Check data content
    if not history.empty:
        job = history.iloc[0]
        print(f"\nSample Job Data:")
        print(f"  Req Mem: {job.get('req_mem')}")
        print(f"  Max RSS: {job.get('max_rss')}")
        print(f"  Total CPU: {job.get('total_cpu')}")
        print(f"  Elapsed: {job.get('elapsed')}")
        print(f"  NCPUS: {job.get('ncpus')}")
        
    return True

if __name__ == "__main__":
    if test_efficiency_fields():
        print("\n✓ Efficiency fields test passed!")
    else:
        print("\n✗ Efficiency fields test FAILED!")
