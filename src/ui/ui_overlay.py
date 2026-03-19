# src/ui/ui_overlay.py


class UIOverlay:
    """UI overlay for stats and heatmap display."""

    def __init__(self, width=1920, height=1080):
        """Initialize UI overlay."""
        self.width = width
        self.height = height
        self.stats = {
            "fps": 0.0,
            "camera_count": 0,
            "ray_count": 0,
            "coverage_percent": 0.0
        }

    def update_stats(self, fps=None, camera_count=None, ray_count=None, coverage=None):
        """Update stats."""
        if fps is not None:
            self.stats["fps"] = fps
        if camera_count is not None:
            self.stats["camera_count"] = camera_count
        if ray_count is not None:
            self.stats["ray_count"] = ray_count
        if coverage is not None:
            self.stats["coverage_percent"] = coverage

    def get_stats(self):
        """Get stats dictionary."""
        return self.stats

    def render(self):
        """Render UI overlay (placeholder)."""
        pass
