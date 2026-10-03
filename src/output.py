from pathlib import Path
import json

import cv2
import numpy as np


def estimate_room_from_image(image):
    """
    Development baseline estimator.

    This is NOT benchmark-grade geometry.
    It provides a deterministic room estimate from visible structure.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=80,
        minLineLength=100,
        maxLineGap=20,
    )

    horizontal_lengths = []
    vertical_lengths = []

    if lines is not None:
        for line in lines:
            values = np.asarray(line).reshape(-1)

            if len(values) < 4:
                continue

            x1, y1, x2, y2 = values[:4]

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            if dx > 0 and dx > 2 * dy:
                horizontal_lengths.append(dx)

            elif dy > 0 and dy > 2 * dx:
                vertical_lengths.append(dy)

    height, width = gray.shape

    if horizontal_lengths:
        room_width_px = max(horizontal_lengths)
    else:
        room_width_px = width * 0.8

    if vertical_lengths:
        room_height_px = max(vertical_lengths)
    else:
        room_height_px = height * 0.6

    room_width_m = round(room_width_px / width * 6.0, 2)
    room_length_m = round(room_height_px / height * 4.0, 2)

    floor_area = round(room_width_m * room_length_m, 2)

    ceiling_height_m = 2.7

    geometry = {
        "room_width_m": room_width_m,
        "room_length_m": room_length_m,
        "ceiling_height_m": ceiling_height_m,
        "floor_area_m2": floor_area,
        "uncertainty": {
            "room_width_m": [
                round(max(0.0, room_width_m - 0.25), 2),
                round(room_width_m + 0.25, 2),
            ],
            "room_length_m": [
                round(max(0.0, room_length_m - 0.25), 2),
                round(room_length_m + 0.25, 2),
            ],
            "ceiling_height_m": [
                2.65,
                2.75,
            ],
        },
        "estimator": "opencv_hough_baseline",
        "benchmark_ready": False,
    }

    return geometry


def create_room_plan(geometry, output_path):
    """
    Create a simple top-down room plan.
    """

    width_m = geometry["room_width_m"]
    length_m = geometry["room_length_m"]

    scale = 100

    canvas_width = int(width_m * scale + 200)
    canvas_height = int(length_m * scale + 200)

    canvas = np.ones(
        (canvas_height, canvas_width, 3),
        dtype=np.uint8,
    ) * 255

    x1 = 100
    y1 = 100

    x2 = int(x1 + width_m * scale)
    y2 = int(y1 + length_m * scale)

    cv2.rectangle(
        canvas,
        (x1, y1),
        (x2, y2),
        (0, 0, 0),
        3,
    )

    cv2.putText(
        canvas,
        f"{width_m:.2f} m",
        (x1 + 20, y1 - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.putText(
        canvas,
        f"{length_m:.2f} m",
        (x2 + 10, (y1 + y2) // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.putText(
        canvas,
        f"Area: {geometry['floor_area_m2']:.2f} m2",
        (x1 + 20, y2 + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.imwrite(str(output_path), canvas)


def save_room_output(geometry, output_dir):
    """
    Save JSON output and rendered room plan.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "result.json"
    image_path = output_dir / "room_plan.png"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            geometry,
            f,
            indent=2,
        )

    create_room_plan(
        geometry,
        image_path,
    )

    return json_path, image_path