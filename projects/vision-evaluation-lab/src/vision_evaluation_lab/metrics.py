from __future__ import annotations

from collections import defaultdict

from .models import BoundingBox, ClassMetrics, DetectionMatch, VisionConfig, VisionSample, VisionSampleResult


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def bbox_iou(left: BoundingBox, right: BoundingBox) -> float:
    x_min = max(left.x_min, right.x_min)
    y_min = max(left.y_min, right.y_min)
    x_max = min(left.x_max, right.x_max)
    y_max = min(left.y_max, right.y_max)
    intersection = max(0.0, x_max - x_min) * max(0.0, y_max - y_min)
    union = left.area + right.area - intersection
    return safe_divide(intersection, union)


def _f1(precision: float, recall: float) -> float:
    return safe_divide(2 * precision * recall, precision + recall)


def classification_metrics(samples: list[VisionSample]) -> list[ClassMetrics]:
    labels = sorted(
        {sample.ground_truth_label for sample in samples}
        | {sample.predicted_label for sample in samples}
    )
    metrics = []
    for label in labels:
        tp = sum(
            sample.ground_truth_label == label and sample.predicted_label == label
            for sample in samples
        )
        fp = sum(
            sample.ground_truth_label != label and sample.predicted_label == label
            for sample in samples
        )
        fn = sum(
            sample.ground_truth_label == label and sample.predicted_label != label
            for sample in samples
        )
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        metrics.append(
            ClassMetrics(
                label=label,
                true_positive=tp,
                false_positive=fp,
                false_negative=fn,
                precision=precision,
                recall=recall,
                f1=_f1(precision, recall),
                support=sum(sample.ground_truth_label == label for sample in samples),
            )
        )
    return metrics


def evaluate_sample(sample: VisionSample, config: VisionConfig) -> VisionSampleResult:
    predictions = [
        box
        for box in sample.predicted_boxes
        if box.confidence is None or box.confidence >= config.min_confidence
    ]
    candidate_pairs = []
    for truth_index, truth_box in enumerate(sample.ground_truth_boxes):
        for prediction_index, predicted_box in enumerate(predictions):
            if truth_box.label != predicted_box.label:
                continue
            iou = bbox_iou(truth_box, predicted_box)
            if iou >= config.iou_threshold:
                candidate_pairs.append((iou, truth_index, prediction_index, truth_box.label))

    matches = []
    used_truth: set[int] = set()
    used_predictions: set[int] = set()
    for iou, truth_index, prediction_index, label in sorted(candidate_pairs, reverse=True):
        if truth_index in used_truth or prediction_index in used_predictions:
            continue
        used_truth.add(truth_index)
        used_predictions.add(prediction_index)
        matches.append(
            DetectionMatch(
                image_id=sample.image_id,
                label=label,
                truth_index=truth_index,
                prediction_index=prediction_index,
                iou=iou,
            )
        )

    return VisionSampleResult(
        image_id=sample.image_id,
        classification_correct=sample.ground_truth_label == sample.predicted_label,
        matches=matches,
        false_positive_boxes=len(predictions) - len(used_predictions),
        false_negative_boxes=len(sample.ground_truth_boxes) - len(used_truth),
    )


def aggregate_detection_metrics(results: list[VisionSampleResult]) -> tuple[float, float, float, float]:
    true_positive = sum(len(result.matches) for result in results)
    false_positive = sum(result.false_positive_boxes for result in results)
    false_negative = sum(result.false_negative_boxes for result in results)
    precision = safe_divide(true_positive, true_positive + false_positive)
    recall = safe_divide(true_positive, true_positive + false_negative)
    mean_iou = safe_divide(
        sum(match.iou for result in results for match in result.matches),
        true_positive,
    )
    return precision, recall, _f1(precision, recall), mean_iou


def detection_metrics_by_label(results: list[VisionSampleResult]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for result in results:
        for match in result.matches:
            counts[match.label] += 1
    return dict(sorted(counts.items()))
