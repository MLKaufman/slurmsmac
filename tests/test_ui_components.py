#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test UI component initialization"""

from slurmsmac.main import Dashboard
from slurmsmac.slurm_data import MockSlurmDataCollector
from textual.widgets import DataTable, Tabs

def test_ui_components():
    """Test that UI components can be initialized."""
    print("Testing UI Components...")

    # Test Dashboard initialization
    print("\n1. Testing Dashboard initialization...")
    app = Dashboard()
    print(f"  ✓ Dashboard created")
    print(f"  ✓ Data collector type: {type(app.data_collector).__name__}")
    print(f"  ✓ Is mock mode: {app.is_mock_mode}")
    print(f"  ✓ Refresh interval: {app.refresh_interval}s")

    # Test that we can call compose (creates the UI structure)
    print("\n2. Testing compose method...")
    widgets = list(app.compose())
    print(f"  ✓ Number of widgets created: {len(widgets)}")
    widget_types = [type(w).__name__ for w in widgets]
    print(f"  ✓ Widget types: {', '.join(widget_types)}")
    
    # Verify key components are present in the yield
    # Note: compose yields top level widgets. Nested ones aren't directly in this list usually unless yielded directly.
    # Based on main.py, it yields Header, Tabs, TabPane, Footer.
    
    has_tabs = any(isinstance(w, Tabs) for w in widgets)
    if has_tabs:
        print("  ✓ Tabs widget found")
    else:
        print("  ✗ Tabs widget NOT found")
        return False

    print("\n✓ All UI component tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_ui_components()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
