import numpy as np
import pytest


@pytest.fixture
def blank_frame():
    """640x480 black frame — no faces."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def small_frame():
    """100x100 black frame."""
    return np.zeros((100, 100, 3), dtype=np.uint8)


@pytest.fixture
def fake_yunet_detection():
    """Factory for a 1x15 YuNet detection row with configurable fields."""
    def _make(x=50, y=60, w=120, h=130, score=0.95):
        det = np.zeros((1, 15), dtype=np.float32)
        det[0, 0:4] = [x, y, w, h]
        det[0, 14] = score
        return det
    return _make
