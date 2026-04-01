from __future__ import annotations

from pathlib import Path
import unittest

from src.pipeline_runner import run_local_pipeline


class RecommendationSystemKubeflowTestCase(unittest.TestCase):
    def test_pipeline_contract(self) -> None:
        result = run_local_pipeline(Path(__file__).resolve().parents[1])
        self.assertIn("validation", result)
        self.assertIn("top_recommendations", result)
        self.assertGreater(result["validation"]["interaction_count"], 10)
        self.assertGreaterEqual(len(result["top_recommendations"]), 3)


if __name__ == "__main__":
    unittest.main()
