# tests/test_ui_overlay.py
import pytest
from src.ui.ui_overlay import UIOverlay


def test_ui_overlay_init():
    """Test UIOverlay initialization."""
    overlay = UIOverlay()
    assert overlay.width == 1920
    assert overlay.height == 1080


def test_ui_overlay_stats():
    """Test stats update."""
    overlay = UIOverlay()
    overlay.update_stats(fps=60.0, camera_count=2, ray_count=5000)
    stats = overlay.get_stats()
    assert stats["fps"] == 60.0
    assert stats["camera_count"] == 2
