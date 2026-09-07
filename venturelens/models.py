"""Small, explicit data models shared by the app and tests."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StartupInfo:
    startup_name: str = "Untitled idea"
    problem: str = ""
    target_customer: str = ""
    proposed_solution: str = ""
    value_proposition: str = ""
    competitors_or_alternatives: list[str] = field(default_factory=list)
    adoption_considerations: list[str] = field(default_factory=list)
    feasibility_considerations: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StartupInfo":
        """Validate untrusted AI output without inventing missing information."""
        if not isinstance(data, dict):
            raise ValueError("AI response was not a JSON object")

        def text(key: str) -> str:
            value = data.get(key, "")
            return value.strip()[:2_000] if isinstance(value, str) else ""

        def items(key: str) -> list[str]:
            value = data.get(key, [])
            if not isinstance(value, list):
                return []
            return [str(item).strip()[:300] for item in value if str(item).strip()][:8]

        return cls(
            startup_name=text("startup_name") or "Untitled idea",
            problem=text("problem"),
            target_customer=text("target_customer"),
            proposed_solution=text("proposed_solution"),
            value_proposition=text("value_proposition"),
            competitors_or_alternatives=items("competitors_or_alternatives"),
            adoption_considerations=items("adoption_considerations"),
            feasibility_considerations=items("feasibility_considerations"),
        )


@dataclass
class AIAnalysis:
    explanations: dict[str, str]
    strengths: list[str]
    risks: list[str]
    biggest_adoption_risk: str
    questions: list[str]
