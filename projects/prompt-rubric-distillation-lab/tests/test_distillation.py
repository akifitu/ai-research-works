from __future__ import annotations

import unittest

from prompt_rubric_distillation_lab.distillation import (
    ambiguity_flags,
    infer_dimension,
    infer_scale_type,
)


class DistillationTests(unittest.TestCase):
    def test_infers_factuality_dimension_from_grounding_language(self) -> None:
        text = "Every major claim must be supported by cited evidence and be factually accurate."
        self.assertEqual("factuality", infer_dimension(text))

    def test_detects_ambiguous_quality_language(self) -> None:
        text = "The answer should be clear, concise, and high quality."
        flags = ambiguity_flags(text)

        self.assertIn("clear", flags)
        self.assertIn("concise", flags)
        self.assertIn("quality", flags)

    def test_binary_scale_detected_for_explicit_requirements(self) -> None:
        text = "The answer must avoid harmful suggestions."
        self.assertEqual("binary", infer_scale_type(text))


if __name__ == "__main__":
    unittest.main()
