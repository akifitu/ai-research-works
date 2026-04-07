from __future__ import annotations

import unittest

from vision_evaluation_lab.metrics import bbox_iou
from vision_evaluation_lab.models import BoundingBox


class GeometryTests(unittest.TestCase):
    def test_bbox_iou_handles_overlap(self) -> None:
        left = BoundingBox("box", 0, 0, 10, 10)
        right = BoundingBox("box", 5, 5, 15, 15)

        self.assertAlmostEqual(25 / 175, bbox_iou(left, right), places=5)

    def test_bbox_iou_handles_disjoint_boxes(self) -> None:
        left = BoundingBox("box", 0, 0, 10, 10)
        right = BoundingBox("box", 20, 20, 30, 30)

        self.assertEqual(0.0, bbox_iou(left, right))


if __name__ == "__main__":
    unittest.main()
