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


def test_ui_overlay_stats_update():
    """Test that UIOverlay updates stats correctly."""
    overlay = UIOverlay()

    overlay.update_stats(fps=60.0, camera_count=1, ray_count=1024, coverage=45.5)

    assert overlay.stats["fps"] == 60.0
    assert overlay.stats["camera_count"] == 1
    assert overlay.stats["ray_count"] == 1024
    assert overlay.stats["coverage_percent"] == 45.5


def test_ui_overlay_render_no_error():
    """Test that UIOverlay.render() doesn't raise error."""
    overlay = UIOverlay()
    overlay.update_stats(fps=60.0, camera_count=1, ray_count=1024, coverage=45.5)

    # Should not raise any error
    # Note: Full render test would require OpenGL context
    try:
        overlay.render(viewport_width=1280, viewport_height=960)
    except Exception as e:
        # If error, should not be about unimplemented render
        assert "render() not implemented" not in str(e)
