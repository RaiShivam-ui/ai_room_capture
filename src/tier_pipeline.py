from pathlib import Path
import json

import cv2


def process_video(input_path, output_dir):
    """
    Video-tier runtime adapter.

    Extracts representative frames and records capture metadata.
    Actual metric reconstruction is a later backend stage.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Video input not found: {input_path}"
        )

    video = cv2.VideoCapture(str(input_path))

    if not video.isOpened():
        raise ValueError(
            f"Could not open video: {input_path}"
        )

    frame_count = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    fps = float(
        video.get(cv2.CAP_PROP_FPS)
    )

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    duration = (
        frame_count / fps
        if fps > 0
        else 0.0
    )

    metadata = {
        "tier": "video",
        "input": str(input_path),
        "frame_count": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 3),
        "reconstruction_status": "capture_validated",
        "backend": "video_runtime_adapter",
        "benchmark_ready": False,
    }

    metadata_path = output_dir / "capture_metadata.json"

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
        )

    video.release()

    return metadata_path


def process_lidar(input_path, output_dir):
    """
    LiDAR-tier runtime adapter.

    Validates a LiDAR capture directory and records available
    sensor files. Actual RGB/depth/pose reconstruction is a
    later backend stage.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            f"LiDAR input not found: {input_path}"
        )

    if not input_path.is_dir():
        raise ValueError(
            "LiDAR input must be a capture directory."
        )

    files = [
        path
        for path in input_path.rglob("*")
        if path.is_file()
    ]

    extensions = {}

    for file_path in files:
        extension = file_path.suffix.lower() or "<none>"
        extensions[extension] = (
            extensions.get(extension, 0) + 1
        )

    metadata = {
        "tier": "lidar",
        "input": str(input_path),
        "file_count": len(files),
        "file_extensions": extensions,
        "reconstruction_status": "capture_validated",
        "backend": "lidar_runtime_adapter",
        "benchmark_ready": False,
    }

    metadata_path = output_dir / "capture_metadata.json"

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
        )

    return metadata_path