from pathlib import Path
import json

import cv2
import numpy as np


def detect_openings(image):
    """
    Development opening detector.

    Detects large rectangular candidate regions from a single image.
    Metric dimensions remain uncalibrated until camera/scene scale
    is available.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(
        gray,
        100,
        255,
        cv2.THRESH_BINARY_INV,
    )

    kernel = np.ones((5, 5), np.uint8)

    binary = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
    )

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    image_height, image_width = gray.shape

    candidates = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        area = w * h

        if area < 12000:
            continue

        if w < 80 or h < 100:
            continue

        if x <= 5 or y <= 5:
            continue

        if x + w >= image_width - 5:
            continue

        if y + h >= image_height - 5:
            continue

        aspect_ratio = w / h

        if aspect_ratio < 0.35 or aspect_ratio > 2.5:
            continue

        # Very tall rectangles are likely doors.
        if h > w * 1.4:
            opening_type = "door"
            confidence = 0.80

        # Wider rectangles are likely windows.
        elif w > h * 1.2:
            opening_type = "window"
            confidence = 0.75

        else:
            continue

        candidates.append(
            {
                "type": opening_type,
                "bbox_px": [
                    int(x),
                    int(y),
                    int(x + w),
                    int(y + h),
                ],
                "width_px": int(w),
                "height_px": int(h),
                "confidence": confidence,
                "measurement_status": "uncalibrated",
                "width_m": None,
                "height_m": None,
            }
        )

    # Remove overlapping duplicate detections.
    candidates.sort(
        key=lambda item: (
            item["width_px"] * item["height_px"]
        ),
        reverse=True,
    )

    openings = []

    for candidate in candidates:
        x1, y1, x2, y2 = candidate["bbox_px"]

        duplicate = False

        for existing in openings:
            ex1, ey1, ex2, ey2 = existing["bbox_px"]

            intersection_x1 = max(x1, ex1)
            intersection_y1 = max(y1, ey1)
            intersection_x2 = min(x2, ex2)
            intersection_y2 = min(y2, ey2)

            if (
                intersection_x2 > intersection_x1
                and intersection_y2 > intersection_y1
            ):
                duplicate = True
                break

        if not duplicate:
            candidate["id"] = (
                f"{candidate['type']}_{len(openings) + 1}"
            )
            openings.append(candidate)

    return openings


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

            if dx > 2 * dy:
                horizontal_lengths.append(dx)

            elif dy > 2 * dx:
                vertical_lengths.append(dy)

    height, width = gray.shape

    room_width_px = (
        max(horizontal_lengths)
        if horizontal_lengths
        else width * 0.8
    )

    room_length_px = (
        max(vertical_lengths)
        if vertical_lengths
        else height * 0.6
    )

    room_width_m = round(
        room_width_px / width * 6.0,
        2,
    )

    room_length_m = round(
        room_length_px / height * 4.0,
        2,
    )

    floor_area = round(
        room_width_m * room_length_m,
        2,
    )

    openings = detect_openings(image)

    geometry = {
        "schema_version": "0.3",

        "room": {
            "id": "room_1",

            "dimensions": {
                "width_m": room_width_m,
                "length_m": room_length_m,
                "ceiling_height_m": 2.70,
                "floor_area_m2": floor_area,
            },

            "uncertainty": {
                "width_m": [
                    round(
                        max(0, room_width_m - 0.25),
                        2,
                    ),
                    round(
                        room_width_m + 0.25,
                        2,
                    ),
                ],

                "length_m": [
                    round(
                        max(0, room_length_m - 0.25),
                        2,
                    ),
                    round(
                        room_length_m + 0.25,
                        2,
                    ),
                ],

                "ceiling_height_m": [
                    2.65,
                    2.75,
                ],

                "floor_area_m2": [
                    round(
                        max(0, floor_area - 1.0),
                        2,
                    ),
                    round(
                        floor_area + 1.0,
                        2,
                    ),
                ],
            },

            "openings": openings,

            "surfaces": {
                "walls": [],
                "floor": {
                    "area_m2": floor_area,
                },
                "ceiling": {
                    "height_m": 2.70,
                },
            },

            "damage": [],

            "concealed_damage": {
                "status": "unknown",
                "flags": [],
                "rule": None,
            },

            "scope": [],

            "confidence": {
                "overall": 0.30,
                "geometry": 0.25,
                "openings": (
                    min(1.0, len(openings) / 2)
                    if openings
                    else 0.0
                ),
                "damage": 0.0,
            },
        },

        "property": {
            "rooms": ["room_1"],
            "adjacency": [],
        },

        "provenance": {
            "estimator": "opencv_hough_baseline",
            "opening_detector": "opencv_contour_baseline",
            "source_type": "photo",
            "benchmark_ready": False,
            "metric_calibration": "not_available",
            "note": (
                "Development baseline only. "
                "Measurements are not benchmark ground truth."
            ),
        },
    }

    return geometry


def create_room_plan(geometry, output_path):
    dimensions = geometry["room"]["dimensions"]

    width_m = dimensions["width_m"]
    length_m = dimensions["length_m"]

    scale = 100

    canvas_width = int(
        width_m * scale + 200
    )

    canvas_height = int(
        length_m * scale + 200
    )

    canvas = np.ones(
        (
            canvas_height,
            canvas_width,
            3,
        ),
        dtype=np.uint8,
    ) * 255

    x1 = 100
    y1 = 100

    x2 = int(
        x1 + width_m * scale
    )

    y2 = int(
        y1 + length_m * scale
    )

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
        f"Area: {dimensions['floor_area_m2']:.2f} m2",
        (x1 + 20, y2 + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.imwrite(
        str(output_path),
        canvas,
    )


def save_room_output(geometry, output_dir):
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = output_dir / "result.json"
    image_path = output_dir / "room_plan.png"

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as f:
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