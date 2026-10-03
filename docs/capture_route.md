\# AI Room Capture — Capture Route \& Device Matrix



\## 1. Capture Tiers



| Tier | Capture Method | Device Requirement | Input | Current Pipeline | Target Reconstruction |

|---|---|---|---|---|---|

| Tier 1 | Still photographs | iPhone 15+ | 2–8 unordered room photographs | OpenCV feature matching + geometry baseline | Pose-free wide-baseline MVS |

| Tier 2 | Handheld walkthrough video | iPhone 15+ | RGB video | Video capture-validation adapter | Visual tracking + depth + global optimization |

| Tier 3 | LiDAR capture | LiDAR-enabled Pro device | Depth + RGB + poses + intrinsics | LiDAR capture-validation adapter | Raw sensor geometry + global optimization |



\---



\## 2. Tier 1 — Photos



\### Capture procedure



1\. Select one room.

2\. Capture between 2 and 8 still photographs.

3\. Cover the room from multiple viewpoints.

4\. Include walls, floor, ceiling and visible openings where possible.

5\. Avoid relying on a single frontal image.

6\. Store all photographs for one room in the same capture directory.



Example:



```text

data/

└── captures/

&#x20;   └── photos/

&#x20;       └── room\_001/

&#x20;           ├── room\_001\_01.jpg

&#x20;           ├── room\_001\_02.jpg

&#x20;           ├── room\_001\_03.jpg

&#x20;           └── room\_001\_04.jpg

