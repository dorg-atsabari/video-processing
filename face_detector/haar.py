import cv2
from .base import BaseFaceDetector


class HaarFaceDetector(BaseFaceDetector):
    """Face detector using improved Haar Cascade (optimized for face detection)."""

    def __init__(self, **kwargs):
        print("Using improved Haar Cascade face detector (optimized for faces)")
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.haar_scale_factor = 1.1
        self.haar_min_neighbors = 10

    def _is_valid_face(self, x, y, w, h, frame_width, frame_height):
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < 0.7 or aspect_ratio > 1.3:
            return False
        if w > frame_width * 0.5:
            return False
        if (y + h / 2) > frame_height * 0.85:
            return False
        return True

    def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
        faces = []
        frame_height, frame_width = frame_img.shape[:2]
        min_size = int(round(min_size))

        gray = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        detected = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.haar_scale_factor,
            minNeighbors=self.haar_min_neighbors,
            minSize=(min_size, min_size),
            maxSize=(int(frame_width * 0.5), int(frame_height * 0.5))
        )

        for (x, y, w, h) in detected:
            if w < min_size or h < min_size:
                continue
            if self._is_valid_face(x, y, w, h, frame_width, frame_height):
                faces.append((x, y, w, h))

        return faces
