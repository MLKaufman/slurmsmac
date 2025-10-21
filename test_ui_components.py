#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test UI component initialization"""

from src.slurmsmac.main import Dashboard, JobStats
from src.slurmsmac.slurm_data import MockSlurmDataCollector

def test_ui_components():
    """Test that UI components can be initialized."""
    print("Testing UI Components...")

    # Test JobStats widget
    print("\n1. Testing JobStats widget...")
    stat_widget = JobStats("Test Stat", "42")
    print(f"  ✓ JobStats created: title='{stat_widget.title}', value='{stat_widget.value}'")

    # Test Dashboard initialization
    print("\n2. Testing Dashboard initialization...")
    app = Dashboard()
    print(f"  ✓ Dashboard created")
    print(f"  ✓ Data collector type: {type(app.data_collector).__name__}")
    print(f"  ✓ Is mock mode: {app.is_mock_mode}")
    print(f"  ✓ Refresh interval: {app.refresh_interval}s")

    # Test that stat widgets are initialized
    print("\n3. Testing internal stat widgets...")
    print(f"  ✓ total_jobs_stat: {app.total_jobs_stat.title}")
    print(f"  ✓ active_jobs_stat: {app.active_jobs_stat.title}")
    print(f"  ✓ completed_jobs_stat: {app.completed_jobs_stat.title}")
    print(f"  ✓ failed_jobs_stat: {app.failed_jobs_stat.title}")

    # Test that we can call compose (creates the UI structure)
    print("\n4. Testing compose method...")
    widgets = list(app.compose())
    print(f"  ✓ Number of widgets created: {len(widgets)}")
    widget_types = [type(w).__name__ for w in widgets]
    print(f"  ✓ Widget types: {', '.join(widget_types)}")

    print("\n✓ All UI component tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_ui_components()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
