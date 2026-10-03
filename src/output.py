from pathlib import Path
import json

import cv2
import numpy as np

FIX_LOOP_VERSION = "edge_refined_v1"


def _intersection_over_union(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    intersection_width = max(0, ix2 - ix1)
    intersection_height = max(0, iy2 - iy1)
    intersection = intersection_width * intersection_height

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union = area_a + area_b - intersection

    if union == 0:
        return 0.0

    return intersection / union


def _edge_support(edges, x, y, w, h):
    """
    Measure how strongly the candidate boundary is supported by image edges.
    """

    image_height, image_width = edges.shape

    margin = max(3, int(min(w, h) * 0.03))

    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(image_width, x + w + margin)
    y2 = min(image_height, y + h + margin)

    region = edges[y1:y2, x1:x2]

    if region.size == 0:
        return 0.0

    return float(np.mean(region > 0))


def detect_openings(image):
    """
    Development opening detector.

    Uses contour geometry plus edge-support scoring to reduce weak
    rectangular false positives.

    Metric dimensions remain uncalibrated until camera/scene scale
    is available.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(
        blurred,
        50,
        150,
    )

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

        # Fix Loop refinement:
        # reject irregular contours whose occupied area is too small
        # relative to their bounding rectangle.
        contour_area = cv2.contourArea(contour)

        if contour_area <= 0:
            continue

        rectangularity = contour_area / float(area)

        if rectangularity < 0.55:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter <= 0:
            continue

        approx = cv2.approxPolyDP(
            contour,
            0.03 * perimeter,
            True,
        )

        polygon_support = min(
            1.0,
            len(approx) / 4.0,
        )

        edge_support = _edge_support(
            edges,
            x,
            y,
            w,
            h,
        )

        if edge_support < 0.015:
            continue

        geometric_score = min(
            1.0,
            rectangularity * 1.25,
        )

        confidence = (
            0.45 * geometric_score
            + 0.30 * polygon_support
            + 0.25 * min(1.0, edge_support * 8.0)
        )

        if h > w * 1.4:
            opening_type = "door"

        elif w > h * 1.2:
            opening_type = "window"

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
                "confidence": round(
                    float(confidence),
                    3,
                ),
                "measurement_status": "uncalibrated",
                "width_m": None,
                "height_m": None,
                "rectangularity": round(
                    float(rectangularity),
                    3,
                ),
                "edge_support": round(
                    float(edge_support),
                    3,
                ),
            }
        )

    candidates.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    openings = []

    for candidate in candidates:
        candidate_box = candidate["bbox_px"]

        duplicate = False

        for existing in openings:
            existing_box = existing["bbox_px"]

            if _intersection_over_union(
                candidate_box,
                existing_box,
            ) > 0.35:
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

            if dx > dy * 3:
                horizontal_lengths.append(dx)

            elif dy > dx * 3:
                vertical_lengths.append(dy)

    if horizontal_lengths:
        image_width_px = max(horizontal_lengths)
    else:
        image_width_px = image.shape[1]

    if vertical_lengths:
        image_height_px = max(vertical_lengths)
    else:
        image_height_px = image.shape[0]

    # Development-only normalization.
    # These values are NOT calibrated measurements.
    width_m = round(
        6.0 * image_width_px / image.shape[1],
        2,
    )

    length_m = round(
        4.0 * image_height_px / image.shape[0],
        2,
    )

    ceiling_height_m = 2.70

    floor_area_m2 = round(
        width_m * length_m,
        2,
    )

    openings = detect_openings(image)

    result = {
        "schema_version": "0.3",

        "dimensions": {
            "width_m": width_m,
            "length_m": length_m,
            "ceiling_height_m": ceiling_height_m,
            "floor_area_m2": floor_area_m2,
        },

        "uncertainty": {
            "width_m": None,
            "length_m": None,
            "ceiling_height_m": None,
            "floor_area_m2": None,
        },

        "openings": openings,

        "surfaces": [
            {
                "id": "floor_1",
                "type": "floor",
                "area_m2": floor_area_m2,
                "confidence": 0.5,
            },
            {
                "id": "wall_1",
                "type": "wall",
                "area_m2": None,
                "confidence": 0.4,
            },
            {
                "id": "wall_2",
                "type": "wall",
                "area_m2": None,
                "confidence": 0.4,
            },
            {
                "id": "wall_3",
                "type": "wall",
                "area_m2": None,
                "confidence": 0.4,
            },
            {
                "id": "wall_4",
                "type": "wall",
                "area_m2": None,
                "confidence": 0.4,
            },
            {
                "id": "ceiling_1",
                "type": "ceiling",
                "area_m2": floor_area_m2,
                "confidence": 0.5,
            },
        ],

        "damage": [],

        "concealed_damage": {
            "flag": False,
            "rule": "No concealed damage inference in development baseline.",
            "confidence": 0.0,
        },

        "scope": [],

        "confidence": {
            "overall": 0.45,
            "geometry": 0.35,
            "openings": (
                round(
                    float(
                        np.mean(
                            [
                                opening["confidence"]
                                for opening in openings
                            ]
                        )
                    ),
                    3,
                )
                if openings
                else 0.0
            ),
        },

        "provenance": {
            "estimator": "opencv_hough_baseline",
            "opening_detector": "opencv_contour_baseline",
            "fix_loop_version": FIX_LOOP_VERSION,
            "benchmark_ready": False,
            "metric_calibration": "not_available",
            "note": (
                "Development baseline only. Measurements are not "
                "benchmark ground truth."
            ),
        },
    }

    return result


def create_room_plan(image, result):
    """
    Create a simple rendered room plan for development evidence.
    """

    height, width = image.shape[:2]

    canvas = np.ones(
        (height, width, 3),
        dtype=np.uint8,
    ) * 255

    room_width = int(width * 0.75)
    room_height = int(height * 0.60)

    start_x = int((width - room_width) / 2)
    start_y = int((height - room_height) / 2)

    end_x = start_x + room_width
    end_y = start_y + room_height

    cv2.rectangle(
        canvas,
        (start_x, start_y),
        (end_x, end_y),
        (0, 0, 0),
        4,
    )

    cv2.putText(
        canvas,
        f"Width: {result['dimensions']['width_m']} m",
        (start_x, start_y - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.putText(
        canvas,
        f"Length: {result['dimensions']['length_m']} m",
        (start_x, end_y + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    for opening in result.get("openings", []):
        x1, y1, x2, y2 = opening["bbox_px"]

        cv2.rectangle(
            canvas,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2,
        )

        cv2.putText(
            canvas,
            opening["type"],
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
        )

    return canvas


def save_room_output(
    result,
    output_dir,
):
    """
    Save structured JSON output and rendered plan.
    """

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = output_dir / "result.json"
    plan_path = output_dir / "room_plan.png"

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    # Create a simple rendered plan from the structured result.
    canvas = np.ones(
        (700, 1000, 3),
        dtype=np.uint8,
    ) * 255

    room_width = 750
    room_height = 420

    start_x = 125
    start_y = 140

    end_x = start_x + room_width
    end_y = start_y + room_height

    cv2.rectangle(
        canvas,
        (start_x, start_y),
        (end_x, end_y),
        (0, 0, 0),
        4,
    )

    cv2.putText(
        canvas,
        f"Width: {result['dimensions']['width_m']} m",
        (start_x, start_y - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    cv2.putText(
        canvas,
        f"Length: {result['dimensions']['length_m']} m",
        (start_x, end_y + 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    for opening in result.get("openings", []):
        x1, y1, x2, y2 = opening["bbox_px"]

        cv2.rectangle(
            canvas,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2,
        )

        cv2.putText(
            canvas,
            opening["type"],
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
        )

    cv2.imwrite(
        str(plan_path),
        canvas,
    )

    return json_path, plan_path