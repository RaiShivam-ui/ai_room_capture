\# Fix Loop Iteration 001 — Before / After



\## Target



Opening detection robustness in the Tier 1 photo pipeline.



\## Baseline



The baseline detector used contour-based geometric filtering to identify

rectangular opening candidates.



\## Proposed Improvement



An experimental refinement was implemented using:



\- contour rectangularity

\- polygon approximation

\- image-edge support

\- confidence scoring

\- IoU-based duplicate suppression



\## Result



The development fixture produced the same two opening detections before and

after the attempted refinement:



\- one door candidate

\- one window candidate



The detected pixel bounding boxes were unchanged.



\## Interpretation



The attempted refinement did not produce a measurable improvement on this

development fixture.



This is recorded as a negative result rather than being presented as a

benchmark improvement.



\## Benchmark Status



This experiment is \*\*development-only\*\*.



The case-study benchmark requires measured ground truth, including laser/tape

measurements. No benchmark accuracy claim is made from this fixture.



\## Next Technical Step



The next meaningful improvement should introduce metric calibration and

multi-view opening refinement rather than relying solely on single-image

contours.



Potential approaches include:



1\. multi-view consistency

2\. calibrated camera geometry

3\. local edge refinement around opening boundaries

4\. 3D surface registration

5\. uncertainty propagation into opening measurements



\## Reproduction



Before and after artifacts are stored under:



```text

reports/fix\_loop/

