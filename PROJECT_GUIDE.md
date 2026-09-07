# VentureLens Project Guide

## Architecture and data flow

The Streamlit form collects a name, description, and optional customer and problem. If an API key is available, an LLM converts that text into a fixed `StartupInfo` structure. Missing information stays unknown. Python then scores the five dimensions with transparent rules. Only after scoring may the LLM explain the fixed numbers. Streamlit renders the summary, scores, risks, and research questions.

This separation matters because language models generate plausible language rather than repeatable measurements. Keeping the score in Python makes the same structured input produce the same number and makes the rule inspectable.

## Structured data model

| Field | Meaning | Example | Why it helps |
|---|---|---|---|
| `startup_name` | Short label | QueueLess | Identifies the idea |
| `problem` | User difficulty | Students lose lunch time in queues | Tests problem clarity |
| `target_customer` | Intended user | Students at crowded schools | Prevents “everyone” targeting |
| `proposed_solution` | What will be built | A timed preorder app | Connects problem to action |
| `value_proposition` | Reason to choose it | Recover more lunch time | Tests motivation to switch |
| `competitors_or_alternatives` | Current choices | Waiting, bringing lunch | Avoids pretending there is no competition |
| `adoption_considerations` | Barriers to trying it | School approval | Surfaces behavior and trust issues |
| `feasibility_considerations` | Barriers to building it | Payment integration | Surfaces practical constraints |

Equivalent JSON:

```json
{
  "startup_name": "QueueLess",
  "problem": "Students lose lunch time in queues",
  "target_customer": "Students at crowded schools",
  "proposed_solution": "A timed preorder app",
  "value_proposition": "Recover more lunch time",
  "competitors_or_alternatives": ["waiting", "bringing lunch"],
  "adoption_considerations": ["school approval"],
  "feasibility_considerations": ["payment integration"]
}
```

## Test plan

| Case | Example input | Expected behavior and display | Main failure to watch |
|---|---|---|---|
| Strong idea | Specific problem, customer, alternatives, barriers | All sections and comparatively strong scores | Fluent text mistaken for evidence |
| Weak idea | “An app that does everything” | Low scores and research questions | AI inventing specifics |
| Vague idea | “Make school better” | Unknown fields remain visible | False precision |
| Missing customer | Solution but no user | Customer score near minimum | Inferred customer shown as fact |
| Missing problem | Feature description only | Problem score near minimum | Feature reworded as a problem |
| Competitive idea | Food delivery app | Alternatives retained and discussed | Competition confused with popularity |
| Innovative but unclear customer | New sensor with no buyer | Customer risk highlighted | Novelty inflates all scores |
| Social impact | Food-waste exchange | Same rubric and neutral language | Mission treated as proof of adoption |
| Unrealistic idea | Teleportation service | Feasibility weakness shown | Technical claims accepted uncritically |
| Everyday idea | Neighborhood tutoring marketplace | Balanced result and next questions | Generic advice |
| Empty description | Blank form | Clear validation error | Crash or API call |
| API/network failure | Valid idea, unavailable service | Visible offline-mode message | Silent fabrication |

The tests reveal the central weakness: text completeness is not market evidence. A detailed but false idea can outscore a short but well-researched one. The proposed evidence log is the most useful next improvement.

## Interview preparation

**60-second explanation:** VentureLens helps someone examine a startup idea across five areas: the problem, customer, competition, value proposition, and adoption and feasibility. The optional AI turns a natural-language description into structured fields. A deterministic Python rubric then calculates every score, so the language model cannot invent or change the numbers. AI may explain those fixed scores, and Streamlit displays the result, risks, and questions to investigate. The score does not predict success; it helps reveal missing assumptions. Building it taught me why reliable AI applications need validation, clear ownership of decisions, and graceful failure handling.

**Two-minute explanation:** Start with the 60-second explanation, then show one example from the interface. Open `scoring.py` and demonstrate how missing customer information becomes a low, repeatable score. Explain that LLM output is untrusted: it is parsed, normalized, and rejected if its shape is wrong. Finish with the limitation that specificity is not proof, and describe the evidence-log improvement.

### Difficult questions and honest answers

1. **Why use AI at all?** Natural-language extraction and readable explanations are useful, but the app still works without AI.
2. **Is the score scientifically validated?** No. It is a transparent educational rubric, not a predictive model.
3. **Why equal weights?** They are easy to understand and avoid pretending I know empirically correct weights.
4. **Can a user game it with long text?** Yes. Detail can increase scores, which is why the next version should distinguish claims from evidence.
5. **How do you stop hallucinations?** Prompts require unknowns, responses are validated, and invalid output triggers offline mode. This reduces—not eliminates—the risk.
6. **Why not let the LLM score?** Its output can vary and its reasoning is hard to audit. Python makes the rule repeatable.
7. **What happens when the API fails?** The user sees a message and the deterministic scorer uses only form data.
8. **What is technically interesting?** The boundary between probabilistic extraction and deterministic decision logic, plus validation at that boundary.
9. **What would you test next?** Real examples with human reviewers, especially whether extracted fields preserve unknowns and whether explanations match scores.
10. **What one improvement matters most?** An evidence log tied to each assumption, because it improves the meaning of the score without adding predictive claims.

## Critical admissions style review

The genuinely interesting element is not the dashboard; it is the explicit boundary around AI. The basic parts are the Streamlit form and length-based rubric. The project would appear superficial if it claimed to judge commercial promise, forecast adoption, or perform market analysis. An interviewer will challenge the validity of the rubric, the role of AI, repeatability, and whether the student understands failure modes. The strongest learning signal is being able to trace one input through extraction, validation, scoring, fallback, and display. Avoid README claims such as “predicts success,” “AI-powered market research,” or “unbiased evaluation.” The evidence-log improvement adds the most intellectual depth for the least complexity.
