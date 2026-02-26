"""
Face detection module using improved Haar Cascade.
Provides a simple interface for face detection in video frames.
"""
import os
import cv2


class FaceDetector:
    """Face detector using improved Haar Cascade (optimized for face detection)."""
    
    def __init__(self, model_dir="."):
        """
        Initialize face detector.
        
        Args:
            model_dir: Directory for model files (not used, kept for compatibility)
        """
        self.face_cascade = None
        
        # Use improved Haar Cascade for face detection
        # Note: YOLOv8 general model detects "person" not "face", so we use Haar Cascade
        # which is specifically designed for face detection and gives proper face-sized boxes
        print("Using improved Haar Cascade face detector (optimized for faces)")
        self._init_haar_cascade()
    
    def _init_haar_cascade(self):
        """Initialize Haar Cascade classifier with improved parameters."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # Improved parameters for better detection (reduced false positives)
        self.haar_scale_factor = 1.1   # Slightly larger = fewer false positives
        self.haar_min_neighbors = 10    # Higher = fewer false positives (was 6)
    
    def _is_valid_face(self, x, y, w, h, frame_width, frame_height):
        """
        Validate if detection is likely a face based on heuristics.
        
        Args:
            x, y, w, h: Bounding box coordinates
            frame_width, frame_height: Frame dimensions
        
        Returns:
            True if detection appears to be a valid face
        """
        # Check aspect ratio - faces are typically roughly square or slightly taller
        # Typical face aspect ratio: 0.7 to 1.3 (width/height)
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < 0.7 or aspect_ratio > 1.3:
            return False
        
        # Check size - faces shouldn't be too large relative to frame
        # Max face width should be reasonable (e.g., < 50% of frame width)
        max_face_width = frame_width * 0.5
        if w > max_face_width:
            return False
        
        # Check position - faces are typically in upper 2/3 of frame
        # (people's faces are usually not at the very bottom)
        face_center_y = y + h / 2
        if face_center_y > frame_height * 0.85:  # Too low in frame
            return False
        
        return True
    
    def detect_faces(self, frame_img, min_confidence=0.8, min_size=80):
        """
        Detect faces in a frame with validation to filter false positives and strictly ignore detections below min_size.

        Args:
            frame_img: BGR image frame (numpy array)
            min_confidence: Minimum confidence for detection (unused in Haar, kept for compatibility)
            min_size: Minimum face width (and height) in pixels to consider valid. (int or convertible to int)

        Returns:
            List of tuples (x, y, w, h) for detected faces, or empty list if none found
        """
        faces = []
        frame_height, frame_width = frame_img.shape[:2]

        # Ensure min_size is an integer
        min_size = int(round(min_size))

        # Use improved Haar Cascade for face detection
        gray = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        detected = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.haar_scale_factor,
            minNeighbors=self.haar_min_neighbors,
            minSize=(min_size, min_size),  # Filter small faces early (strict)
            maxSize=(int(frame_width * 0.5), int(frame_height * 0.5))
        )

        for (x, y, w, h) in detected:
            # Strictly reject if width OR height is smaller than min_size
            if w < min_size or h < min_size:
                continue  # Skip this detection - too small

            if self._is_valid_face(x, y, w, h, frame_width, frame_height):
                faces.append((x, y, w, h))
        return faces
    
    def get_first_face(self, frame_img, min_confidence=0.5, min_size=100):
        """
        Get the first (most confident) face detection.
        
        Args:
            frame_img: BGR image frame (numpy array)
            min_confidence: Minimum confidence for DNN detection (0.0-1.0)
            min_size: Minimum face width in pixels to consider valid
        
        Returns:
            Tuple (x, y, w, h) for the first face, or None if no face detected
        """
        faces = self.detect_faces(frame_img, min_confidence, min_size)
        return faces[0] if faces else None

