"""Optional LLM extraction and explanation with strict score ownership."""

import json
import os
from pathlib import Path

from .models import AIAnalysis, StartupInfo


class AIServiceError(RuntimeError):
    pass


EXTRACTION_SYSTEM = """You extract only structured facts about a startup idea.
Return JSON with exactly these keys: startup_name, problem, target_customer,
proposed_solution, value_proposition, competitors_or_alternatives,
adoption_considerations, feasibility_considerations. The last three are arrays.
Use only user-provided information or clearly label an inference with 'Inference:'.
Use empty strings or arrays for unknown facts. Never treat marketing claims as evidence."""

ANALYSIS_SYSTEM = """You explain a deterministic startup evaluation for a student.
The numerical scores are fixed by Python: never change, recalculate, round, or dispute them.
Return JSON with: explanations (an object keyed by the five score names), strengths
(exactly 3 strings), risks (exactly 3 strings), biggest_adoption_risk (one string),
and questions (exactly 3 strings). Distinguish supplied facts, inference, and unknowns."""


def enrich_with_ai(base: StartupInfo, description: str) -> tuple[StartupInfo, AIAnalysis | None]:
    _load_local_env()
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    api_key = groq_key or openai_key
    if not api_key:
        raise AIServiceError("No Groq or OpenAI API key was found, so VentureLens used its transparent offline scoring mode.")
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1" if groq_key else None,
            timeout=20.0,
            max_retries=1,
        )
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b") if groq_key else os.getenv("OPENAI_MODEL", "gpt-5-mini")
        extraction = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": json.dumps({"form_fields": base.__dict__, "description": description})},
            ],
        )
        info = StartupInfo.from_dict(_parse_json(extraction.choices[0].message.content or ""))
        # Explicit form entries are more trustworthy than an omission by the model.
        info.startup_name = base.startup_name if base.startup_name != "Untitled idea" else info.startup_name
        info.problem = base.problem or info.problem
        info.target_customer = base.target_customer or info.target_customer
        info.proposed_solution = info.proposed_solution or base.proposed_solution

        # Scores are computed here in Python and supplied to the explainer as immutable facts.
        from .scoring import evaluate

        scores = evaluate(info).scores
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM},
                {"role": "user", "content": json.dumps({"startup": info.__dict__, "fixed_scores": scores})},
            ],
        )
        analysis = _validate_analysis(_parse_json(response.choices[0].message.content or ""), scores)
        return info, analysis
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AIServiceError("The AI returned an invalid response, so VentureLens used offline mode.") from exc
    except Exception as exc:
        raise AIServiceError("The AI service was unavailable, so VentureLens used offline mode.") from exc


def _load_local_env() -> None:
    """Load KEY=VALUE pairs from the project's private .env file."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            os.environ.setdefault(key, value)


def _parse_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        if cleaned.lstrip().startswith("json"):
            cleaned = cleaned.lstrip()[4:].lstrip()
    value = json.loads(cleaned)
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    return value


def _validate_analysis(data: dict, scores: dict[str, int]) -> AIAnalysis:
    explanations = data.get("explanations")
    if not isinstance(explanations, dict) or set(explanations) != set(scores):
        raise ValueError("Invalid explanations")

    def exact_list(key: str) -> list[str]:
        value = data.get(key)
        if not isinstance(value, list) or len(value) != 3 or not all(isinstance(x, str) and x.strip() for x in value):
            raise ValueError(f"Invalid {key}")
        return [x.strip()[:600] for x in value]

    biggest = data.get("biggest_adoption_risk")
    if not isinstance(biggest, str) or not biggest.strip():
        raise ValueError("Invalid biggest adoption risk")
    return AIAnalysis(
        explanations={key: str(explanations[key]).strip()[:800] for key in scores},
        strengths=exact_list("strengths"),
        risks=exact_list("risks"),
        biggest_adoption_risk=biggest.strip()[:800],
        questions=exact_list("questions"),
    )
