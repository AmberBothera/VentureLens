# VentureLens

VentureLens is an educational Streamlit app that helps a student examine how clearly a startup idea addresses adoption-related questions.

## Why I built it

Startup ideas can sound exciting before their assumptions are made visible. I built VentureLens to turn an informal idea into a consistent set of questions about the problem, customer, alternatives, value, and practical adoption. It is a portfolio project about AI-assisted decision support, not a professional venture-capital tool.

## How it works

```text
User idea → optional LLM extraction → structured startup data
          → deterministic Python rubric → five scores and overall score
          → optional LLM explanation → Streamlit results
```

The LLM has two limited roles: it can structure natural-language input and explain the fixed result. Python owns all numerical scoring. If the API is unavailable or its response is invalid, the app reports that and uses an offline result instead of silently fabricating information.

## The five dimensions

- **Problem:** how clearly a meaningful problem is described
- **Customer:** how specifically the intended user is defined
- **Competition:** whether current alternatives are acknowledged
- **Value Proposition:** whether there is a clear reason to choose the solution
- **Adoption & Feasibility:** whether barriers and implementation constraints are considered

Each dimension receives 1–10 using a visible rule: 1–2 weak or unclear, 3–4 limited, 5–6 reasonable, 7–8 strong, and 9–10 exceptional. The dimensions have equal weight, so `overall = sum(five scores) × 2`.

## Technology

- Python and dataclasses for data and scoring
- Streamlit for the interface
- OpenAI Responses API as an optional AI layer
- Python's built-in `unittest` for automated checks

## Example

For a school lunch preordering idea, VentureLens displays a score for each dimension, an overall score, reasons tied to supplied evidence, three strengths, three risks, the largest adoption risk, and three questions for a user interview or small pilot.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional; then load these variables in your shell
streamlit run app.py
```

To use the AI features, export `OPENAI_API_KEY`. Without it, the app still runs in transparent offline mode.

Run tests with:

```bash
python -m unittest discover -s tests
```

## Limitations

The rubric mainly rewards completeness and specificity, not verified market truth. AI extraction can misunderstand text. No score predicts demand, revenue, or success, and the app does not perform market research. A user should validate assumptions with interviews, observation, and small experiments.

## What I learned

This project taught me to separate probabilistic AI tasks from deterministic program logic, validate untrusted model output, design graceful fallbacks, and communicate uncertainty. It also showed me that a numerical result is only useful when its assumptions are visible.

## Future improvements

The highest-value next step is an evidence log: users could attach an interview quote or experiment result to each assumption, and the rubric could distinguish a claim from observed evidence without becoming a prediction system.
