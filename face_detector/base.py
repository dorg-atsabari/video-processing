from abc import ABC, abstractmethod


class BaseFaceDetector(ABC):
    """Abstract base class defining the face detector interface."""

    @abstractmethod
    def detect_faces(self, frame_img, min_confidence=0.5, min_size=80):
        """
        Detect faces in a frame.

        Args:
            frame_img: BGR image frame (numpy array)
            min_confidence: Minimum detection confidence (0.0-1.0)
            min_size: Minimum face width in pixels

        Returns:
            List of (x, y, w, h) tuples
        """

    def get_first_face(self, frame_img, min_confidence=0.5, min_size=100):
        """
        Get the first detected face.

        Args:
            frame_img: BGR image frame (numpy array)
            min_confidence: Minimum detection confidence (0.0-1.0)
            min_size: Minimum face width in pixels

        Returns:
            (x, y, w, h) tuple or None if no face detected
        """
        faces = self.detect_faces(frame_img, min_confidence, min_size)
        return faces[0] if faces else None
