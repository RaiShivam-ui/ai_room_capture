import argparse
from pathlib import Path

import cv2

from src.photo_pipeline import (
    analyze_images,
    load_images,
    match_images,
    estimate_transforms,
)


def stitch_images(images):
    """Create a panorama from the captured room images."""
    if len(images) < 2:
        return images[0][1] if images else None

    image_list = [image for _, image in images]

    stitcher = cv2.Stitcher_create()
    status, panorama = stitcher.stitch(image_list)

    if status != cv2.Stitcher_OK:
        return None

    return panorama


def main():
    parser = argparse.ArgumentParser(
        description="AI Room Capture"
    )

    parser.add_argument(
        "--tier",
        required=True,
        choices=["photos", "video", "lidar"],
    )

    parser.add_argument("--input", required=True)

    args = parser.parse_args()

    if args.tier == "photos":
        images = load_images(args.input)

        if not images:
            raise ValueError(
                f"No images found in {args.input}"
            )

        result = analyze_images(args.input)

        print(f"Images processed: {result['image_count']}")

        matches = match_images(images)

        print("\nFeature matching:")

        for match in matches:
            print(
                f"{match['image_a']} -> "
                f"{match['image_b']}: "
                f"{match['good_matches']} good matches"
            )

        transforms = estimate_transforms(images)

        print("\nGeometric transforms:")

        for transform in transforms:
            if transform["success"]:
                print(
                    f"{transform['image_a']} -> "
                    f"{transform['image_b']}: "
                    f"{transform['inliers']} inliers "
                    f"({transform['inlier_ratio']:.1%})"
                )
            else:
                print(
                    f"{transform['image_a']} -> "
                    f"{transform['image_b']}: "
                    f"FAILED - {transform['reason']}"
                )

        panorama = stitch_images(images)

        if panorama is None:
            print("\nPanorama stitching failed.")
            return

        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "photo_panorama.jpg"

        cv2.imwrite(
            str(output_path),
            panorama,
        )

        print(f"\nPanorama saved to: {output_path}")

    else:
        print(
            f"Tier '{args.tier}' is not implemented yet."
        )


if __name__ == "__main__":
    main()