"""Streamlit entry point for VentureLens."""

import streamlit as st

from venturelens.ai import AIServiceError, enrich_with_ai
from venturelens.models import StartupInfo
from venturelens.scoring import evaluate


st.set_page_config(page_title="VentureLens", page_icon="🔎", layout="wide")
st.title("VentureLens")
st.caption("AI Startup Idea Evaluator")

with st.form("idea_form"):
    st.subheader("Enter Your Idea")
    name = st.text_input("Startup idea name", max_chars=100)
    description = st.text_area(
        "Description",
        height=160,
        max_chars=4_000,
        placeholder="What does the idea do, who is it for, and why would they use it?",
    )
    customer = st.text_input("Target customer (optional)", max_chars=300)
    problem = st.text_input("Problem (optional)", max_chars=500)
    submitted = st.form_submit_button("Evaluate My Idea", type="primary")

if submitted:
    if not description.strip():
        st.error("Please describe your startup idea before evaluating it.")
        st.stop()

    base = StartupInfo(
        startup_name=name.strip() or "Untitled idea",
        problem=problem.strip(),
        target_customer=customer.strip(),
        proposed_solution=description.strip(),
        value_proposition="",
        competitors_or_alternatives=[],
        adoption_considerations=[],
        feasibility_considerations=[],
    )

    ai_note = None
    try:
        info, ai_analysis = enrich_with_ai(base, description)
    except AIServiceError as exc:
        info, ai_analysis = base, None
        ai_note = str(exc)

    result = evaluate(info)

    st.subheader("Startup Summary")
    summary = {
        "Startup name": info.startup_name,
        "Problem": info.problem or "Unknown",
        "Target customer": info.target_customer or "Unknown",
        "Proposed solution": info.proposed_solution or "Unknown",
        "Value proposition": info.value_proposition or "Unknown",
        "Competitors or alternatives": ", ".join(info.competitors_or_alternatives) or "Unknown",
        "Adoption considerations": ", ".join(info.adoption_considerations) or "Unknown",
        "Feasibility considerations": ", ".join(info.feasibility_considerations) or "Unknown",
    }
    for label, value in summary.items():
        st.markdown(f"**{label}:** {value}")
    if ai_note:
        st.info(ai_note)

    st.subheader("VentureLens Score")
    st.metric("Overall score", f"{result.overall}/100")
    cols = st.columns(5)
    for col, (dimension, score) in zip(cols, result.scores.items()):
        col.metric(dimension, f"{score}/10")

    st.markdown("#### Why these scores?")
    explanations = ai_analysis.explanations if ai_analysis else result.explanations
    for dimension, explanation in explanations.items():
        st.markdown(f"**{dimension} ({result.scores[dimension]}/10):** {explanation}")

    strengths = ai_analysis.strengths if ai_analysis else result.strengths
    risks = ai_analysis.risks if ai_analysis else result.risks
    biggest_risk = ai_analysis.biggest_adoption_risk if ai_analysis else result.biggest_adoption_risk
    questions = ai_analysis.questions if ai_analysis else result.questions

    st.subheader("What Looks Strong")
    for item in strengths:
        st.markdown(f"- {item}")

    st.subheader("What Could Go Wrong")
    for item in risks:
        st.markdown(f"- {item}")

    st.subheader("Biggest Adoption Risk")
    st.warning(biggest_risk)

    st.subheader("What Should I Investigate Next?")
    for item in questions:
        st.markdown(f"- {item}")

st.divider()
st.subheader("Disclaimer")
st.write(
    "VentureLens is an educational decision-support tool. Its rubric highlights "
    "questions and assumptions; it does not predict startup success or provide investment advice."
)
