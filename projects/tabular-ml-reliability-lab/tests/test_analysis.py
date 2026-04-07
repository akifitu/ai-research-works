from __future__ import annotations

import unittest

from tabular_ml_reliability_lab.analysis import detect_leakage_candidates, profile_dataset


class AnalysisTests(unittest.TestCase):
    def test_profile_dataset_infers_numeric_feature(self) -> None:
        profiles = profile_dataset([{"age": 30}, {"age": 40}, {"age": None}])
        by_name = {profile.name: profile for profile in profiles}

        self.assertEqual("numeric", by_name["age"].kind)
        self.assertAlmostEqual(35.0, by_name["age"].mean)
        self.assertAlmostEqual(1 / 3, by_name["age"].missing_rate)

    def test_detect_leakage_candidates_checks_name_and_values(self) -> None:
        rows = [
            {"target": "yes", "target_copy": "yes", "noise": "a"},
            {"target": "no", "target_copy": "no", "noise": "b"},
        ]

        self.assertEqual(["target_copy"], detect_leakage_candidates(rows, "target"))


if __name__ == "__main__":
    unittest.main()
