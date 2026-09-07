"""Transparent deterministic scoring; no LLM chooses or changes a score."""

from dataclasses import dataclass

from .models import StartupInfo

DIMENSIONS = (
    "Problem",
    "Customer",
    "Competition",
    "Value Proposition",
    "Adoption & Feasibility",
)


@dataclass
class Evaluation:
    scores: dict[str, int]
    overall: int
    explanations: dict[str, str]
    strengths: list[str]
    risks: list[str]
    biggest_adoption_risk: str
    questions: list[str]


def _detail_score(text: str, *, strong: int = 8) -> int:
    """Map amount of supplied detail to 1–strong; absence always scores 1."""
    words = len(text.split())
    if words == 0:
        return 1
    if words < 5:
        return 3
    if words < 12:
        return 5
    if words < 25:
        return 7
    return strong


def _list_score(items: list[str]) -> int:
    if not items:
        return 1
    if len(items) == 1:
        return 5
    if len(items) == 2:
        return 7
    return 9


def evaluate(info: StartupInfo) -> Evaluation:
    """Score five dimensions on 1–10 and scale their equal-weight sum to 100."""
    problem = _detail_score(info.problem, strong=9)
    customer = _detail_score(info.target_customer, strong=9)
    competition = _list_score(info.competitors_or_alternatives)

    value = _detail_score(info.value_proposition, strong=9)
    if info.value_proposition and info.target_customer:
        value = min(10, value + 1)

    adoption = round(
        (_list_score(info.adoption_considerations) + _list_score(info.feasibility_considerations)) / 2
    )
    if not info.proposed_solution:
        adoption = 1

    scores = dict(zip(DIMENSIONS, (problem, customer, competition, value, adoption)))
    overall = sum(scores.values()) * 2  # five 1–10 scores; equal weight; range 10–100

    explanations = {
        "Problem": _why(problem, "problem description"),
        "Customer": _why(customer, "target-customer definition"),
        "Competition": _why(competition, "identified alternatives"),
        "Value Proposition": _why(value, "reason a customer would choose the solution"),
        "Adoption & Feasibility": _why(adoption, "adoption barriers and implementation constraints"),
    }
    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    strengths = [f"{name} is one of the clearest areas in the information supplied." for name, _ in ranked[:3]]
    weakest = sorted(scores.items(), key=lambda pair: pair[1])[:3]
    risks = [f"{name} needs stronger evidence or more specific detail." for name, _ in weakest]
    biggest = (
        "The largest adoption risk is that the intended customer and reason to switch are not yet proven."
        if customer <= value
        else "The largest adoption risk is that the proposed value may not overcome existing habits or alternatives."
    )
    questions = [
        "Which five potential users can you interview, and what evidence would change your mind?",
        "What do those users do today instead of using this idea?",
        "What is the smallest test that would show whether someone will try or pay for it?",
    ]
    return Evaluation(scores, overall, explanations, strengths, risks, biggest, questions)


def _why(score: int, evidence: str) -> str:
    band = "weak or unclear" if score <= 2 else "limited" if score <= 4 else "reasonable" if score <= 6 else "strong" if score <= 8 else "exceptional"
    return f"The supplied {evidence} is {band} under the published rubric. Missing details are treated as unknown, not guessed."
