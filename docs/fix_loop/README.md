\# Fix Loop



\## Purpose



This directory documents the iterative improvement process required by the

case study.



Each fix-loop iteration must contain:



1\. Worst gate identified

2\. Root-cause hypothesis

3\. Evidence supporting the hypothesis

4\. Proposed fix

5\. Prediction before implementation

6\. Updated implementation

7\. Regenerated before/after outputs

8\. Measured comparison



The benchmark specification requires a regenerable and readable before/after

comparison. A fix without regenerated evidence is not treated as a completed

fix-loop iteration.



\---



\## Iteration 001 — Development Baseline



\### Status



Planned.



\### Current evidence



The current photo pipeline uses:



\- ORB feature matching

\- RANSAC geometric verification

\- OpenCV-based structural geometry

\- contour-based opening detection



Opening detections currently remain in pixel coordinates and are explicitly

marked as uncalibrated.



\### Limitation



The current development fixture does not contain laser/tape ground-truth

measurements.



Therefore it cannot be used to claim compliance with the benchmark opening

accuracy gate.



\### Root-cause hypothesis



The current opening detector relies on image-space contours and simple

geometric filtering. This can produce candidates whose dimensions are useful

for development diagnostics but are not sufficient for calibrated metric

measurement.



\### Proposed fix



The next improvement should separate:



1\. opening candidate detection

2\. geometric refinement

3\. metric calibration

4\. uncertainty estimation



rather than treating a raw image contour as a final measured opening.



\### Prediction



After refinement and calibration infrastructure are added:



\- opening geometry should become more stable across image views

\- measurements should be expressed in metric units

\- uncertainty should reflect calibration and detection quality

\- benchmark opening-width evaluation should become possible once ground truth

&#x20; is available



\### Evidence policy



No numerical benchmark improvement is claimed until a real benchmark capture

and corresponding laser/tape measurement are available.



\---



\## Before/After Evidence Contract



Every completed iteration should produce:



```text

reports/

└── fix\_loop/

&#x20;   └── iteration\_XXX/

&#x20;       ├── before/

&#x20;       ├── after/

&#x20;       ├── metrics\_before.json

&#x20;       ├── metrics\_after.json

&#x20;       └── diff.md

