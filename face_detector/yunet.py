import os
import cv2
from .base import BaseFaceDetector

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet_2023mar.onnx")


class YuNetFaceDetector(BaseFaceDetector):
    """Face detector using OpenCV's YuNet (cv2.FaceDetectorYN)."""

    def __init__(self, model_path=DEFAULT_MODEL_PATH, **kwargs):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"YuNet model not found at: {model_path}\n"
                f"Download it from: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet"
            )
        print(f"Using YuNet face detector (model: {model_path})")
        self._detector = cv2.FaceDetectorYN.create(model_path, "", (320, 320))
        self._last_input_size = (320, 320)

    def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
        frame_height, frame_width = frame_img.shape[:2]
        min_size = int(round(min_size))

        if (frame_width, frame_height) != self._last_input_size:
            self._detector.setInputSize((frame_width, frame_height))
            self._last_input_size = (frame_width, frame_height)

        _, detections = self._detector.detect(frame_img)

        if detections is None:
            return []

        faces = []
        for det in detections:
            x, y, w, h, score = int(det[0]), int(det[1]), int(det[2]), int(det[3]), float(det[14])
            if score < min_confidence:
                continue
            if w < min_size or h < min_size:
                continue
            faces.append((x, y, w, h))

        return faces
