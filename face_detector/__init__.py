from .haar import HaarFaceDetector
from .yunet import YuNetFaceDetector


def create_face_detector(backend="yunet", **kwargs):
    """
    Factory function for face detectors.

    Args:
        backend: "yunet" (default) or "haar"
        **kwargs: Backend-specific options (e.g. model_path for yunet)

    Returns:
        A face detector instance with detect_faces() and get_first_face() methods
    """
    if backend == "yunet":
        return YuNetFaceDetector(**kwargs)
    elif backend == "haar":
        return HaarFaceDetector(**kwargs)
    else:
        raise ValueError(f"Unknown face detector backend: '{backend}'. Choose 'yunet' or 'haar'.")
