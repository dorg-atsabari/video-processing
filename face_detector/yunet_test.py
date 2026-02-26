import numpy as np
import pytest
from unittest.mock import MagicMock
from face_detector.yunet import YuNetFaceDetector, DEFAULT_MODEL_PATH


@pytest.fixture
def detector():
    return YuNetFaceDetector()


@pytest.fixture
def detector_with_mock(detector):
    """YuNetFaceDetector with cv2.FaceDetectorYN replaced by a MagicMock."""
    detector._detector = MagicMock()
    return detector


# --- Instantiation ---

def test_instantiation(detector):
    assert detector._last_input_size == (320, 320)


def test_raises_if_model_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="YuNet model not found"):
        YuNetFaceDetector(model_path=str(tmp_path / "missing.onnx"))


def test_default_model_path_inside_package():
    assert "face_detector" in DEFAULT_MODEL_PATH
    assert DEFAULT_MODEL_PATH.endswith(".onnx")


# --- detect_faces ---

def test_detect_faces_returns_list(detector_with_mock, blank_frame):
    detector_with_mock._detector.detect.return_value = (None, None)
    assert isinstance(detector_with_mock.detect_faces(blank_frame), list)


def test_detect_faces_empty_when_no_detections(detector_with_mock, blank_frame):
    detector_with_mock._detector.detect.return_value = (None, None)
    assert detector_with_mock.detect_faces(blank_frame) == []


def test_detect_faces_tuple_format(detector_with_mock, blank_frame, fake_yunet_detection):
    detector_with_mock._detector.detect.return_value = (None, fake_yunet_detection())
    result = detector_with_mock.detect_faces(blank_frame)
    assert len(result) == 1
    assert result[0] == (50, 60, 120, 130)


def test_detect_faces_filters_low_confidence(detector_with_mock, blank_frame, fake_yunet_detection):
    detector_with_mock._detector.detect.return_value = (None, fake_yunet_detection(score=0.3))
    assert detector_with_mock.detect_faces(blank_frame, min_confidence=0.5) == []


def test_detect_faces_filters_small_faces(detector_with_mock, blank_frame, fake_yunet_detection):
    detector_with_mock._detector.detect.return_value = (None, fake_yunet_detection(w=40, h=40))
    assert detector_with_mock.detect_faces(blank_frame, min_size=80) == []


def test_detect_faces_updates_input_size_on_change(detector_with_mock):
    detector_with_mock._detector.detect.return_value = (None, None)
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    frame2 = np.zeros((720, 1280, 3), dtype=np.uint8)

    detector_with_mock.detect_faces(frame1)
    detector_with_mock.detect_faces(frame2)

    assert detector_with_mock._detector.setInputSize.call_count == 2


def test_detect_faces_skips_setInputSize_on_same_size(detector_with_mock):
    detector_with_mock._detector.detect.return_value = (None, None)
    detector_with_mock._last_input_size = (640, 480)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detector_with_mock.detect_faces(frame)

    detector_with_mock._detector.setInputSize.assert_not_called()
