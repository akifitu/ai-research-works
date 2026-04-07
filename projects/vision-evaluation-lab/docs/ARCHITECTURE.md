# Architecture

`vision-evaluation-lab` is intentionally stdlib-first. The goal is not to train
a vision model in the repository baseline; it is to demonstrate evaluation
discipline around model outputs that could come from YOLO, Detectron, SAM, or a
custom classifier.

## Pipeline

1. Load a compact JSON benchmark with image-level labels and detection boxes.
2. Validate boxes into immutable dataclasses.
3. Match predictions to ground truth with greedy IoU assignment.
4. Build classification and detection confusion counts.
5. Emit aggregate metrics suitable for model cards and CI regression checks.

## Extension Points

- Replace JSON input with COCO or Pascal VOC adapters.
- Add segmentation masks and mask IoU when a real mask dataset is available.
- Add confidence calibration curves for deployed classifiers.
- Add failure slice reports by camera, lighting, geography, or device metadata.
