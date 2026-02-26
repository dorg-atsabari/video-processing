import pytest
from face_detector.base import BaseFaceDetector


def test_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        BaseFaceDetector()


def test_get_first_face_returns_none_on_empty(blank_frame):
    class NoFaceDetector(BaseFaceDetector):
        def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
            return []

    assert NoFaceDetector().get_first_face(blank_frame) is None


def test_get_first_face_returns_first_result(blank_frame):
    class MultiFaceDetector(BaseFaceDetector):
        def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
            return [(10, 20, 100, 100), (200, 200, 80, 80)]

    assert MultiFaceDetector().get_first_face(blank_frame) == (10, 20, 100, 100)


def test_get_first_face_forwards_params(blank_frame):
    received = {}

    class RecordingDetector(BaseFaceDetector):
        def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
            received["min_confidence"] = min_confidence
            received["min_size"] = min_size
            return []

    RecordingDetector().get_first_face(blank_frame, min_confidence=0.9, min_size=150)
    assert received["min_confidence"] == 0.9
    assert received["min_size"] == 150
