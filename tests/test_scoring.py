import unittest

from venturelens.models import StartupInfo
from venturelens.scoring import DIMENSIONS, evaluate


def complete_idea() -> StartupInfo:
    return StartupInfo(
        startup_name="QueueLess",
        problem="Students lose limited lunch time while waiting in long cafeteria queues every school day.",
        target_customer="Public high-school students and cafeteria staff at crowded urban schools.",
        proposed_solution="A mobile preorder system that gives students a pickup window and helps staff batch orders.",
        value_proposition="Students recover lunch time while cafeterias spread demand across the lunch period.",
        competitors_or_alternatives=["waiting in line", "school payment apps", "bringing lunch"],
        adoption_considerations=["student phone access", "staff training", "school approval"],
        feasibility_considerations=["menu integration", "payment privacy", "pilot with one lunch period"],
    )


class ScoringTests(unittest.TestCase):
    def test_complete_idea_has_all_dimensions_and_valid_range(self):
        result = evaluate(complete_idea())
        self.assertEqual(tuple(result.scores), DIMENSIONS)
        self.assertTrue(all(1 <= score <= 10 for score in result.scores.values()))
        self.assertTrue(0 <= result.overall <= 100)

    def test_overall_is_equal_weighted_and_deterministic(self):
        first = evaluate(complete_idea())
        second = evaluate(complete_idea())
        self.assertEqual(first.scores, second.scores)
        self.assertEqual(first.overall, sum(first.scores.values()) * 2)
        self.assertEqual(first, second)

    def test_each_missing_field_is_safe(self):
        cases = [
            ({"problem": ""}, "Problem"),
            ({"target_customer": ""}, "Customer"),
            ({"competitors_or_alternatives": []}, "Competition"),
            ({"value_proposition": ""}, "Value Proposition"),
            ({"proposed_solution": ""}, "Adoption & Feasibility"),
        ]
        for change, dimension in cases:
            with self.subTest(dimension=dimension):
                idea = complete_idea()
                for key, value in change.items():
                    setattr(idea, key, value)
                self.assertGreaterEqual(evaluate(idea).scores[dimension], 1)

    def test_empty_idea_does_not_invent_high_scores(self):
        result = evaluate(StartupInfo())
        self.assertEqual(result.overall, 10)
        self.assertEqual(set(result.scores.values()), {1})

    def test_extra_detail_never_pushes_score_above_ten(self):
        idea = complete_idea()
        idea.value_proposition = "specific " * 100
        self.assertLessEqual(evaluate(idea).scores["Value Proposition"], 10)

    def test_untrusted_model_data_is_normalized(self):
        info = StartupInfo.from_dict({"startup_name": 42, "competitors_or_alternatives": "none"})
        self.assertEqual(info.startup_name, "Untitled idea")
        self.assertEqual(info.competitors_or_alternatives, [])


if __name__ == "__main__":
    unittest.main()
