# Vision Evaluation Lab

This lab provides a dependency-light computer vision evaluation scaffold for
portfolio work. It focuses on the mechanics that matter before a heavy training
stack is introduced: bounding-box IoU, one-to-one detection matching, class-level
precision/recall/F1, and dataset-level audit summaries.

## Research Signal

- Object detection matching with configurable IoU thresholds
- Classification confusion accounting without external libraries
- Per-class precision, recall, F1, and support counts
- JSON benchmark and config files for reproducible evaluation
- CLI entry point for producing portable JSON reports

## Example

```powershell
pip install ./projects/vision-evaluation-lab
vision-evaluation-lab --benchmark projects/vision-evaluation-lab/benchmarks/sample_vision_benchmark.json
```

## Layout

```text
vision-evaluation-lab/
|-- benchmarks/sample_vision_benchmark.json
|-- configs/default_vision_eval.json
|-- docs/
|-- src/vision_evaluation_lab/
`-- tests/
```
