from pathlib import Path
import argparse
import json


def absolute_error(predicted, actual):
    return abs(predicted - actual)


def percentage_error(predicted, actual):
    if actual == 0:
        return None

    return abs(predicted - actual) / abs(actual) * 100


def evaluate_dimension(name, predicted, actual, tolerance):
    error = absolute_error(predicted, actual)
    passed = error <= tolerance

    return {
        "metric": name,
        "predicted": predicted,
        "ground_truth": actual,
        "absolute_error": round(error, 4),
        "percentage_error": (
            round(percentage_error(predicted, actual), 2)
            if percentage_error(predicted, actual) is not None
            else None
        ),
        "tolerance": tolerance,
        "pass": passed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate AI Room Capture measurements."
    )

    parser.add_argument(
        "--prediction",
        required=True,
        help="Path to generated result.json",
    )

    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Path to benchmark ground-truth JSON",
    )

    parser.add_argument(
        "--output",
        default="reports/benchmark_result.json",
        help="Path for evaluation report",
    )

    args = parser.parse_args()

    prediction_path = Path(args.prediction)
    ground_truth_path = Path(args.ground_truth)
    output_path = Path(args.output)

    if not prediction_path.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {prediction_path}"
        )

    if not ground_truth_path.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {ground_truth_path}"
        )

    with open(
        prediction_path,
        "r",
        encoding="utf-8",
    ) as f:
        prediction = json.load(f)

    with open(
        ground_truth_path,
        "r",
        encoding="utf-8",
    ) as f:
        ground_truth = json.load(f)

    predicted_dimensions = prediction["room"]["dimensions"]
    actual_dimensions = ground_truth["room"]["dimensions"]

    evaluations = []

    evaluations.append(
        evaluate_dimension(
            "room_width_m",
            predicted_dimensions["width_m"],
            actual_dimensions["width_m"],
            0.08 * actual_dimensions["width_m"],
        )
    )

    evaluations.append(
        evaluate_dimension(
            "room_length_m",
            predicted_dimensions["length_m"],
            actual_dimensions["length_m"],
            0.08 * actual_dimensions["length_m"],
        )
    )

    evaluations.append(
        evaluate_dimension(
            "ceiling_height_m",
            predicted_dimensions["ceiling_height_m"],
            actual_dimensions["ceiling_height_m"],
            0.015,
        )
    )

    report = {
        "prediction": str(prediction_path),
        "ground_truth": str(ground_truth_path),
        "evaluations": evaluations,
        "summary": {
            "total_metrics": len(evaluations),
            "passed_metrics": sum(
                item["pass"]
                for item in evaluations
            ),
            "pass_rate": round(
                sum(item["pass"] for item in evaluations)
                / len(evaluations),
                3,
            ),
        },
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    print("Benchmark evaluation complete.")
    print(f"Report: {output_path}")

    for item in evaluations:
        status = (
            "PASS"
            if item["pass"]
            else "FAIL"
        )

        print(
            f"{status}: "
            f"{item['metric']} | "
            f"error={item['absolute_error']:.4f} | "
            f"tolerance={item['tolerance']:.4f}"
        )


if __name__ == "__main__":
    main()