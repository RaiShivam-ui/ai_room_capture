import argparse


def main():
    parser = argparse.ArgumentParser(description="AI Room Capture")

    parser.add_argument(
        "--tier",
        required=True,
        choices=["photos", "video", "lidar"],
    )

    parser.add_argument("--input", required=True)

    args = parser.parse_args()

    print(f"Capture tier: {args.tier}")
    print(f"Input: {args.input}")


if __name__ == "__main__":
    main()