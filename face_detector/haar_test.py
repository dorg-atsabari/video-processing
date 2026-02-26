import numpy as np
import pytest
from unittest.mock import MagicMock
from face_detector.haar import HaarFaceDetector


@pytest.fixture
def detector():
    return HaarFaceDetector()


@pytest.fixture
def detector_with_mock_cascade(detector):
    """HaarFaceDetector with cv2.CascadeClassifier replaced by a MagicMock."""
    detector.face_cascade = MagicMock()
    return detector


# --- Instantiation ---

def test_instantiation(detector):
    assert detector.haar_scale_factor == 1.1
    assert detector.haar_min_neighbors == 10


# --- detect_faces ---

def test_detect_faces_returns_list(detector, blank_frame):
    assert isinstance(detector.detect_faces(blank_frame), list)


def test_detect_faces_empty_on_blank_frame(detector, blank_frame):
    assert detector.detect_faces(blank_frame) == []


def test_detect_faces_tuple_format(detector_with_mock_cascade, blank_frame):
    detector_with_mock_cascade.face_cascade.detectMultiScale.return_value = [(50, 50, 120, 120)]
    result = detector_with_mock_cascade.detect_faces(blank_frame)
    assert len(result) == 1
    assert len(result[0]) == 4


def test_detect_faces_min_size_filters_small(detector_with_mock_cascade, blank_frame):
    detector_with_mock_cascade.face_cascade.detectMultiScale.return_value = [(50, 50, 50, 50)]
    result = detector_with_mock_cascade.detect_faces(blank_frame, min_size=100)
    assert result == []


def test_detect_faces_min_size_accepts_float(detector, blank_frame):
    result = detector.detect_faces(blank_frame, min_size=80.5)
    assert isinstance(result, list)


# --- _is_valid_face ---

def test_is_valid_face_rejects_wide_aspect_ratio(detector):
    assert detector._is_valid_face(0, 0, 200, 50, 640, 480) is False


def test_is_valid_face_rejects_tall_aspect_ratio(detector):
    assert detector._is_valid_face(0, 0, 50, 200, 640, 480) is False


def test_is_valid_face_rejects_oversized(detector):
    assert detector._is_valid_face(0, 0, 400, 400, 640, 480) is False


def test_is_valid_face_rejects_bottom_of_frame(detector):
    # face center at y=450 in 480-height frame → 450/480 > 85%
    assert detector._is_valid_face(0, 420, 100, 100, 640, 480) is False


def test_is_valid_face_accepts_valid(detector):
    assert detector._is_valid_face(100, 100, 120, 120, 640, 480) is True
