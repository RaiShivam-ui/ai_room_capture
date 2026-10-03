\# AI Room Capture — Compliance Matrix



This document maps the implementation to the requirements defined in the

Applied AI Engineer case study.



Status meanings:



\- \*\*Implemented\*\* — functionality exists in the repository and has been tested.

\- \*\*Partial\*\* — supporting infrastructure exists, but the full requirement is not yet satisfied.

\- \*\*Planned\*\* — architecture/design exists but implementation is pending.

\- \*\*Blocked\*\* — cannot be verified without required benchmark capture or ground truth.

\- \*\*Development-only\*\* — tested only on the synthetic development fixture and not benchmark evidence.



\---



\## 1. Capture Tiers



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Tier 1 — 2–8 unordered room photographs | Partial | Photo pipeline accepts a directory of JPG/JPEG/PNG images. |

| Tier 2 — handheld RGB video | Partial | Video runtime adapter validates video metadata and capture integrity. |

| Tier 3 — LiDAR capture | Partial | LiDAR runtime adapter validates a capture directory and records available files. |

| Same rooms captured across all three tiers | Blocked | Real benchmark capture set has not yet been collected. |

| One command per capture | Implemented | `src/run.py` exposes a single CLI entry point with `--tier` and `--input`. |



\---



\## 2. Spatial Reconstruction



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Per-room dimensioned plan | Partial | Current photo baseline generates a room plan from image geometry. |

| Wall geometry | Partial | OpenCV line-based geometry baseline implemented. |

| Ceiling height | Partial | Current development baseline outputs a 2.70 m estimate; not benchmark-calibrated. |

| Floor area | Partial | Derived from estimated room dimensions. |

| Openings | Partial | Contour-based door/window candidate detector implemented. |

| Multi-room stitched plan | Planned | Global multi-room reconstruction and adjacency optimization remain to be implemented. |

| Correct room adjacency | Planned | Property-level adjacency representation exists in output schema; reconstruction is pending. |

| Metric calibration | Planned | Calibration infrastructure is required for benchmark metric accuracy. |



\---



\## 3. Global Optimization and Drift



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Pose/geometry optimization | Planned | Architecture targets global optimization using a factor-graph approach. |

| Loop closure | Planned | Required for multi-room drift accountability. |

| Pose graph / plane correction | Planned | Required by the benchmark specification. |

| Drift accountability | Blocked | Cannot be benchmark-verified until multi-room captures are available. |

| Ablation: optimization ON/OFF | Planned | Benchmark experiment infrastructure required. |



\---



\## 4. Damage Localization



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Per-surface damage regions | Partial | Output schema supports damage regions but detection is not implemented. |

| Damage class | Partial | Output schema reserves damage classification fields. |

| Metric damage extent | Planned | Requires calibrated 3D surface registration. |

| Concealed-damage flags | Partial | Output schema includes concealed-damage status, flags and rule. |

| Rule for concealed damage | Planned | Domain rule implementation pending. |



\---



\## 5. Confidence and Output Contract



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Confidence interval for every measurement | Partial | Current room geometry includes uncertainty intervals; full measurement coverage is pending. |

| Structured JSON output | Implemented | `result.json` follows the project's spatial output schema. |

| Rendered plan | Implemented | `room\_plan.png` is generated for the current room baseline. |

| Scope line items keyed to surfaces | Partial | Output schema supports scope entries; automated generation remains pending. |

| Provenance | Implemented | Output records estimator, source type, calibration status and benchmark readiness. |



\---



\## 6. Benchmark Gates



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Opening widths ≤2 cm on ≥85% | Blocked | Requires real benchmark capture and laser/tape ground truth. |

| Ceiling height ≤1.5 cm | Blocked | Requires calibrated benchmark measurements. |

| Repeat ceiling-height spread ≤1 cm | Blocked | Requires repeated benchmark captures. |

| Repeat wall measurement ≤1 cm or 0.5% | Blocked | Requires repeated captures and ground truth. |

| Photo whole-property footprint ±8% | Blocked | Requires multi-room benchmark capture. |

| Photo wall lengths ±8% | Blocked | Requires calibrated photo benchmark. |

| Video wall lengths ±3% | Blocked | Requires real handheld video benchmark. |

| Calibration scored | Planned | Benchmark evaluator infrastructure created; calibration data still required. |

| Consumer-app head-to-head | Blocked | Requires benchmark rooms and reference application measurements. |



\---



\## 7. Benchmark Evaluation Infrastructure



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Reproducible evaluator | Implemented | `scripts/benchmark/evaluate.py` |

| Ground-truth comparison | Implemented | Evaluator accepts prediction and ground-truth JSON files. |

| Absolute error | Implemented | Evaluator reports absolute measurement error. |

| Percentage error | Implemented | Evaluator reports percentage error. |

| Metric-specific tolerance | Implemented | Room width/length use 8%; ceiling height uses 1.5 cm. |

| Machine-readable benchmark report | Implemented | Evaluator writes JSON report under `reports/`. |

| Real benchmark results | Blocked | No real benchmark ground-truth dataset is currently available. |



\---



\## 8. Reproducibility



| Requirement | Status | Evidence / Implementation |

|---|---|---|

| Fresh-machine setup documentation | Partial | README and project structure are being developed incrementally. |

| Single-command capture execution | Implemented | `python -m src.run --tier ... --input ...` |

| Dependencies documented | Partial | Core Python environment established; requirements lock/documentation remains to be finalized. |

| Large model weights excluded from Git | Implemented | `.gitignore` excludes common model-weight formats. |

| Reproduction bundle | Planned | Final bundle will contain commands, sample capture and generated outputs. |

| Raw benchmark data | Blocked | Real benchmark capture has not yet been collected. |



\---



\## 9. Process Evidence



| Requirement | Status | Evidence |

|---|---|---|

| Incremental Git commits | Implemented | Development is being committed in incremental milestones. |

| Remote GitHub repository | Implemented | Repository is maintained on GitHub. |

| Meaningful commit history | Implemented | Pipeline development has been split across multiple commits. |

| AI coding-tool disclosure | Planned | Final technical documentation will disclose AI-assisted development where applicable. |

| Regenerable before/after fix loop | Planned | Fix-loop experiment still needs to be implemented. |



\---



\## 10. Current Limitations



The current repository contains a transparent development baseline rather than a

benchmark-complete spatial reconstruction system.



In particular:



1\. The photo geometry estimator is an OpenCV baseline.

2\. Opening measurements are currently pixel-space and explicitly marked

&#x20;  `uncalibrated`.

3\. Video and LiDAR currently provide capture-validation adapters rather than

&#x20;  full reconstruction.

4\. Real benchmark captures and laser/tape ground truth are not yet available.

5\. Therefore, no benchmark accuracy claim is made from the current synthetic

&#x20;  development fixture.



These limitations are intentionally recorded rather than replaced with

unsupported benchmark claims.

