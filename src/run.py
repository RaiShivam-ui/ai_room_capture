import argparse
from pathlib import Path

from src.photo_pipeline import (
    analyze_images,
    load_images,
    match_images,
    estimate_transforms,
)

from src.output import (
    estimate_room_from_image,
    save_room_output,
)


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

        # Temporary development geometry.
        geometry = estimate_room_from_image(
            images[0][1]
        )

        output_dir = Path("outputs") / "test_room"

        json_path, plan_path = save_room_output(
            geometry,
            output_dir,
        )

        print("\nRoom output:")
        print(f"JSON: {json_path}")
        print(f"Plan: {plan_path}")

    else:
        print(
            f"Tier '{args.tier}' is not implemented yet."
        )


if __name__ == "__main__":
    main()