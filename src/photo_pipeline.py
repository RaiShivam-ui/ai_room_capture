from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def load_images(input_dir: str) -> list[tuple[str, np.ndarray]]:
    """Load supported images from a capture directory."""
    directory = Path(input_dir)

    if not directory.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    images = []

    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        image = cv2.imread(str(path))

        if image is not None:
            images.append((path.name, image))

    return images


def analyze_images(input_dir: str) -> dict:
    """Perform basic image-level analysis."""
    images = load_images(input_dir)

    if not images:
        raise ValueError(f"No valid images found in {input_dir}")

    results = []

    for filename, image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        edge_density = float(
            np.count_nonzero(edges) / edges.size
        )

        results.append(
            {
                "filename": filename,
                "width_px": int(image.shape[1]),
                "height_px": int(image.shape[0]),
                "edge_density": round(edge_density, 4),
            }
        )

    return {
        "image_count": len(results),
        "images": results,
    }


def match_images(
    images: list[tuple[str, np.ndarray]]
) -> list[dict]:
    """Find visual correspondences between consecutive images."""

    if len(images) < 2:
        return []

    orb = cv2.ORB_create(nfeatures=2000)

    keypoints = []
    descriptors = []

    for _, image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kp, des = orb.detectAndCompute(gray, None)

        keypoints.append(kp)
        descriptors.append(des)

    matcher = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=True,
    )

    matches_info = []

    for i in range(len(images) - 1):
        if descriptors[i] is None or descriptors[i + 1] is None:
            matches_info.append(
                {
                    "image_a": images[i][0],
                    "image_b": images[i + 1][0],
                    "matches": 0,
                    "good_matches": 0,
                }
            )
            continue

        matches = matcher.match(
            descriptors[i],
            descriptors[i + 1],
        )

        matches = sorted(
            matches,
            key=lambda m: m.distance,
        )

        good_matches = [
            m for m in matches
            if m.distance < 60
        ]

        matches_info.append(
            {
                "image_a": images[i][0],
                "image_b": images[i + 1][0],
                "matches": len(matches),
                "good_matches": len(good_matches),
            }
        )

    return matches_info


def estimate_transforms(
    images: list[tuple[str, np.ndarray]]
) -> list[dict]:
    """Estimate homography between consecutive views."""

    if len(images) < 2:
        return []

    orb = cv2.ORB_create(nfeatures=2000)

    matcher = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=True,
    )

    results = []

    for i in range(len(images) - 1):
        name_a, image_a = images[i]
        name_b, image_b = images[i + 1]

        gray_a = cv2.cvtColor(
            image_a,
            cv2.COLOR_BGR2GRAY,
        )

        gray_b = cv2.cvtColor(
            image_b,
            cv2.COLOR_BGR2GRAY,
        )

        kp_a, des_a = orb.detectAndCompute(
            gray_a,
            None,
        )

        kp_b, des_b = orb.detectAndCompute(
            gray_b,
            None,
        )

        if des_a is None or des_b is None:
            results.append(
                {
                    "image_a": name_a,
                    "image_b": name_b,
                    "success": False,
                    "reason": "insufficient_features",
                }
            )
            continue

        matches = matcher.match(
            des_a,
            des_b,
        )

        good = [
            m for m in matches
            if m.distance < 60
        ]

        if len(good) < 8:
            results.append(
                {
                    "image_a": name_a,
                    "image_b": name_b,
                    "success": False,
                    "reason": "insufficient_matches",
                    "good_matches": len(good),
                }
            )
            continue

        points_a = np.float32(
            [kp_a[m.queryIdx].pt for m in good]
        ).reshape(-1, 1, 2)

        points_b = np.float32(
            [kp_b[m.trainIdx].pt for m in good]
        ).reshape(-1, 1, 2)

        homography, mask = cv2.findHomography(
            points_a,
            points_b,
            cv2.RANSAC,
            5.0,
        )

        if homography is None:
            results.append(
                {
                    "image_a": name_a,
                    "image_b": name_b,
                    "success": False,
                    "reason": "homography_failed",
                    "good_matches": len(good),
                }
            )
            continue

        inliers = (
            int(mask.sum())
            if mask is not None
            else 0
        )

        results.append(
            {
                "image_a": name_a,
                "image_b": name_b,
                "success": True,
                "good_matches": len(good),
                "inliers": inliers,
                "inlier_ratio": round(
                    inliers / len(good),
                    3,
                ),
                "homography": homography.tolist(),
            }
        )

    return results