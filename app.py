import os
import json
from datetime import datetime
 
import pandas as pd
import streamlit as st
from openai import OpenAI
 
 
# ============================================================
# PathBridge AI
# LLM-powered, human-in-the-loop agentic prototype
# ============================================================
 
st.set_page_config(
    page_title="PathBridge AI",
    page_icon="🛡️",
    layout="wide"
)
 
 
# ============================================================
# OpenAI client
# ============================================================
 
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)
 
 
client = get_openai_client()
 
 
# ============================================================
# Model settings
# ============================================================
 
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
 
 
# ============================================================
# Mock workforce data
# In production, this would connect to:
# O*NET, BLS, CareerOneStop, local verified resources
# ============================================================
 
CAREER_PATHWAYS = [
    {
        "title": "Remote Customer Support Representative",
        "category": "Fast income",
        "skills_needed": ["basic computer use", "communication", "email", "customer service"],
        "uses_existing_skills": ["phone communication", "problem solving", "caregiving", "organization"],
        "training_time": "2–4 weeks",
        "mobility_requirement": "low",
        "contact_level": "medium",
        "night_shift_risk": "low",
        "documentation_need": "medium",
        "estimated_wage": "$16–$23/hour",
        "income_speed": "fast",
        "long_term_growth": "medium",
        "notes": "Good for users with limited mobility if they have safe internet/phone access."
    },
    {
        "title": "Medical Billing / Coding Assistant",
        "category": "Stable long-term pathway",
        "skills_needed": ["basic computer use", "attention to detail", "medical terminology"],
        "uses_existing_skills": ["organization", "communication", "record keeping"],
        "training_time": "3–6 months",
        "mobility_requirement": "low",
        "contact_level": "low",
        "night_shift_risk": "low",
        "documentation_need": "medium",
        "estimated_wage": "$18–$28/hour",
        "income_speed": "slow",
        "long_term_growth": "high",
        "notes": "Strong long-term option but may not provide immediate income."
    },
    {
        "title": "Childcare Assistant",
        "category": "Skill-based transition",
        "skills_needed": ["child safety", "basic certification", "communication"],
        "uses_existing_skills": ["caregiving", "patience", "cooking", "cleaning"],
        "training_time": "2–8 weeks",
        "mobility_requirement": "medium",
        "contact_level": "high",
        "night_shift_risk": "low",
        "documentation_need": "high",
        "estimated_wage": "$14–$20/hour",
        "income_speed": "medium",
        "long_term_growth": "medium",
        "notes": "May require background check, transportation, and certification."
    },
    {
        "title": "Food Service Prep / Kitchen Assistant",
        "category": "Immediate local work",
        "skills_needed": ["food safety", "teamwork", "time management"],
        "uses_existing_skills": ["cooking", "cleaning", "organization"],
        "training_time": "1–2 weeks",
        "mobility_requirement": "medium",
        "contact_level": "medium",
        "night_shift_risk": "medium",
        "documentation_need": "low",
        "estimated_wage": "$13–$18/hour",
        "income_speed": "fast",
        "long_term_growth": "low",
        "notes": "Fast entry but may involve stressful environments or late shifts."
    },
    {
        "title": "Administrative Assistant",
        "category": "Office pathway",
        "skills_needed": ["email", "scheduling", "basic computer use", "organization"],
        "uses_existing_skills": ["communication", "record keeping", "organization"],
        "training_time": "4–8 weeks",
        "mobility_requirement": "medium",
        "contact_level": "medium",
        "night_shift_risk": "low",
        "documentation_need": "medium",
        "estimated_wage": "$16–$25/hour",
        "income_speed": "medium",
        "long_term_growth": "medium",
        "notes": "Good pathway if the user can access transportation or remote options."
    },
    {
        "title": "Home Health Aide",
        "category": "Caregiving pathway",
        "skills_needed": ["caregiving", "basic health safety", "certification"],
        "uses_existing_skills": ["caregiving", "cleaning", "communication"],
        "training_time": "4–12 weeks",
        "mobility_requirement": "high",
        "contact_level": "high",
        "night_shift_risk": "medium",
        "documentation_need": "high",
        "estimated_wage": "$15–$22/hour",
        "income_speed": "medium",
        "long_term_growth": "medium",
        "notes": "Uses caregiving skills but may require travel to clients' homes."
    }
]
 
 
# ============================================================
# Session state
# ============================================================
 
if "case_profile" not in st.session_state:
    st.session_state.case_profile = None
 
if "intake_summary" not in st.session_state:
    st.session_state.intake_summary = None
 
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
 
if "advocate_reviews" not in st.session_state:
    st.session_state.advocate_reviews = {}
 
if "final_plan" not in st.session_state:
    st.session_state.final_plan = None
 
 
# ============================================================
# Helper: LLM call
# ============================================================
 
def call_llm(agent_name, instructions, user_input, model_name):
    """
    Calls an LLM agent using OpenAI Responses API.
    If no API key exists or an error occurs, returns a safe fallback.
    """
    if client is None:
        return (
            f"[LLM unavailable: OPENAI_API_KEY not found]\n\n"
            f"{agent_name} could not run. Please set your API key."
        )
 
    try:
        response = client.responses.create(
            model=model_name,
            instructions=instructions,
            input=user_input
        )
        return response.output_text
    except Exception as e:
        return (
            f"[LLM error in {agent_name}]\n\n"
            f"{str(e)}\n\n"
            f"Try checking your API key, model name, internet connection, or billing access."
        )
 
 
# ============================================================
# Rule-based Privacy Guardrail
# ============================================================
 
def privacy_guardrail(profile):
    warnings = []
 
    notes = profile.get("additional_notes", "").lower()
 
    sensitive_terms = [
        "exact address",
        "trafficker name",
        "social security",
        "ssn",
        "passport number",
        "medical diagnosis",
        "immigration status"
    ]
 
    for term in sensitive_terms:
        if term in notes:
            warnings.append(
                f"Potential sensitive detail detected: '{term}'. "
                "Avoid storing unnecessary sensitive information."
            )
 
    if not warnings:
        warnings.append("No obvious unnecessary sensitive details detected.")
 
    return warnings
 
 
# ============================================================
# Rule-based Safety Agent
# ============================================================
 
def safety_agent(profile, pathway):
    flags = []
    risk_score = 0
 
    if profile["mobility"] in ["No car", "Restricted mobility"] and pathway["mobility_requirement"] == "high":
        flags.append("High mobility requirement may make this pathway unsafe or unrealistic.")
        risk_score += 3
 
    if profile["mobility"] == "No car" and pathway["mobility_requirement"] == "medium":
        flags.append("Transportation may be needed; verify safe and reliable access.")
        risk_score += 1
 
    if profile["work_environment"] == "Low-contact" and pathway["contact_level"] == "high":
        flags.append("High-contact environment may conflict with the survivor's preference or trauma-related needs.")
        risk_score += 2
 
    if profile["night_shift"] == "Cannot work nights" and pathway["night_shift_risk"] in ["medium", "high"]:
        flags.append("Possible night-shift or irregular schedule risk.")
        risk_score += 2
 
    if profile["documentation"] == "Limited documentation" and pathway["documentation_need"] == "high":
        flags.append("May require documentation, certification, or background checks.")
        risk_score += 2
 
    if profile["income_timeline"] == "Immediately" and pathway["income_speed"] == "slow":
        flags.append("This pathway may not provide income quickly enough by itself.")
        risk_score += 2
 
    if not flags:
        flags.append("No major safety conflicts detected, but human advocate review is still required.")
 
    if risk_score >= 5:
        risk_level = "High"
    elif risk_score >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"
 
    return risk_level, flags, risk_score
 
 
# ============================================================
# Rule-based Career Scoring Agent
# ============================================================
 
def career_scoring_agent(profile):
    user_skills = set(profile["skills"])
    ranked = []
 
    for pathway in CAREER_PATHWAYS:
        score = 0
 
        pathway_existing_skills = set(pathway["uses_existing_skills"])
        matched_skills = user_skills.intersection(pathway_existing_skills)
        score += len(matched_skills) * 2
 
        if profile["mobility"] in ["No car", "Restricted mobility"]:
            if pathway["mobility_requirement"] == "low":
                score += 4
            elif pathway["mobility_requirement"] == "medium":
                score += 1
            else:
                score -= 4
 
        if profile["income_timeline"] == "Immediately":
            if pathway["income_speed"] == "fast":
                score += 4
            elif pathway["income_speed"] == "medium":
                score += 1
            else:
                score -= 3
 
        if profile["work_environment"] == "Low-contact":
            if pathway["contact_level"] == "low":
                score += 4
            elif pathway["contact_level"] == "medium":
                score += 1
            else:
                score -= 3
 
        if profile["night_shift"] == "Cannot work nights":
            if pathway["night_shift_risk"] == "low":
                score += 2
            else:
                score -= 2
 
        if profile["documentation"] == "Limited documentation":
            if pathway["documentation_need"] == "low":
                score += 2
            elif pathway["documentation_need"] == "high":
                score -= 3
 
        risk_level, flags, risk_score = safety_agent(profile, pathway)
        score -= risk_score
 
        ranked.append({
            **pathway,
            "score": score,
            "matched_skills": list(matched_skills),
            "risk_level": risk_level,
            "safety_flags": flags
        })
 
    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
    return ranked[:3]
 
 
# ============================================================
# LLM Agent 1: Intake / Orchestrator Agent
# ============================================================
 
def llm_intake_agent(profile, model_name):
    instructions = """
You are the Intake and Orchestrator Agent for PathBridge AI.
 
Your task:
- Convert a case worker's structured input and notes into a concise survivor-centered case summary.
- Identify urgent needs, constraints, existing skills, and missing information.
- Use trauma-informed, cautious language.
- Do not give legal, medical, or emergency advice.
- Do not ask for unnecessary sensitive details.
- Do not make final decisions.
 
Return the response using these sections:
1. Case Summary
2. Key Constraints
3. Existing Strengths / Skills
4. Missing Information for Human Advocate
5. Recommended Agents to Run Next
"""
 
    user_input = f"""
Structured case profile:
{json.dumps(profile, indent=2)}
 
Please summarize this case for a support organization.
"""
    return call_llm("Intake / Orchestrator Agent", instructions, user_input, model_name)
 
 
# ============================================================
# LLM Agent 2: Career Explanation Agent
# ============================================================
 
def llm_career_explanation_agent(profile, recommendations, model_name):
    instructions = """
You are the Career Pathway Explanation Agent for PathBridge AI.
 
Your task:
- Explain why each recommended economic pathway may or may not fit.
- Use the survivor's constraints and skills.
- Do not sound certain or authoritative.
- Do not say "best job" or "you should do this."
- Use "possible pathway" and "human advocate should verify."
- Keep safety, feasibility, income timeline, training burden, and documentation needs visible.
- Do not provide legal, medical, or emergency advice.
 
Return:
1. Overview
2. Pathway-by-pathway explanation
3. Key tradeoffs
4. Questions for human advocate review
"""
 
    user_input = f"""
Survivor profile:
{json.dumps(profile, indent=2)}
 
Ranked recommendations:
{json.dumps(recommendations, indent=2)}
 
Explain the recommendations in a trauma-informed way.
"""
    return call_llm("Career Explanation Agent", instructions, user_input, model_name)
 
 
# ============================================================
# LLM Agent 3: Training / Skill Recovery Agent
# ============================================================
 
def llm_training_agent(profile, recommendation, model_name):
    instructions = """
You are the Training and Skill Recovery Agent for PathBridge AI.
 
Your task:
- Create a realistic training and transition plan for one pathway.
- Consider time-to-income, existing skills, missing skills, documentation barriers, mobility, and safety.
- Include short-term and long-term steps if needed.
- Keep the plan practical and non-authoritative.
- Always include human advocate verification.
 
Return:
1. Why this pathway may fit
2. Skills already present
3. Skills or requirements to build
4. Short-term steps
5. Long-term steps
6. Human advocate checks
"""
 
    user_input = f"""
Survivor profile:
{json.dumps(profile, indent=2)}
 
Selected pathway:
{json.dumps(recommendation, indent=2)}
 
Create a training and transition plan.
"""
    return call_llm("Training / Skill Recovery Agent", instructions, user_input, model_name)
 
 
# ============================================================
# LLM Agent 4: Final Plan Agent using Human Feedback
# ============================================================
 
def llm_final_plan_agent(profile, recommendations, advocate_reviews, model_name):
    instructions = """
You are the Final Action Plan Agent for PathBridge AI.
 
Your task:
- Use the AI recommendations, safety flags, and human advocate review decisions.
- Produce a final survivor-centered recovery pathway plan.
- If the advocate selected Modify, revise the plan according to the advocate note.
- If the advocate selected Reject as unsafe, do not include that pathway as a recommended action.
- If the advocate selected Escalate, prioritize human escalation before career planning.
- Make it clear that the survivor and human advocate make final decisions.
- Do not provide legal, medical, therapeutic, or emergency instructions.
- Use cautious, trauma-informed language.
 
Return:
1. Final Reviewed Summary
2. Recommended Short-Term Pathway
3. Recommended Long-Term Pathway
4. Safety and Feasibility Checks
5. Human Advocate Notes Incorporated
6. Next Steps for the Support Organization
7. What the AI Must Not Decide
"""
 
    user_input = f"""
Survivor profile:
{json.dumps(profile, indent=2)}
 
AI recommendations:
{json.dumps(recommendations, indent=2)}
 
Human advocate reviews:
{json.dumps(advocate_reviews, indent=2)}
 
Generate a final reviewed action plan.
"""
    return call_llm("Final Action Plan Agent", instructions, user_input, model_name)
 
 
# ============================================================
# Sidebar
# ============================================================
 
st.sidebar.title("🛡️ PathBridge AI")
st.sidebar.caption("LLM-powered, human-in-the-loop prototype")
 
mode = st.sidebar.radio(
    "Choose interface",
    [
        "1. Case Worker Intake",
        "2. Human Advocate Review",
        "3. Final Reviewed Plan",
        "4. System Architecture"
    ]
)
 
model_name = st.sidebar.text_input("OpenAI model", value=DEFAULT_MODEL)
 
if client is None:
    st.sidebar.error("OPENAI_API_KEY not found.")
else:
    st.sidebar.success("API key detected.")
 
st.sidebar.markdown("---")
st.sidebar.write("Human-in-the-loop required before action.")
 
 
# ============================================================
# Header
# ============================================================
 
st.title("PathBridge AI")
st.subheader("Agentic AI support for survivor-centered economic recovery planning")
 
st.warning(
    "Prototype only. This system provides decision support for trained support organizations. "
    "It does not replace emergency services, legal advice, medical care, therapy, or survivor advocates."
)
 
 
# ============================================================
# Interface 1: Case Worker Intake
# ============================================================
 
if mode == "1. Case Worker Intake":
 
    st.header("Case Worker Intake Interface")
    st.write(
        "This interface is for the case worker or support organization. "
        "It collects only the information needed to generate safe economic recovery options."
    )
 
    col1, col2 = st.columns(2)
 
    with col1:
        employment_history = st.selectbox(
            "Employment history",
            ["Limited", "Some experience", "Stable prior experience"]
        )
 
        education = st.selectbox(
            "Education level",
            ["Less than high school", "High school/GED", "Some college", "College degree"]
        )
 
        mobility = st.selectbox(
            "Mobility / transportation",
            ["No car", "Restricted mobility", "Reliable transportation"]
        )
 
        income_timeline = st.selectbox(
            "How soon is income needed?",
            ["Immediately", "Within 1–3 months", "Long-term planning"]
        )
 
    with col2:
        work_environment = st.selectbox(
            "Preferred work environment",
            ["Low-contact", "Moderate contact", "No preference"]
        )
 
        night_shift = st.selectbox(
            "Night shift availability",
            ["Cannot work nights", "Can work some nights", "No restriction"]
        )
 
        childcare = st.selectbox(
            "Childcare responsibilities?",
            ["Yes", "No", "Unknown"]
        )
 
        documentation = st.selectbox(
            "Documentation status",
            ["Limited documentation", "Basic documents available", "Unknown"]
        )
 
    skills = st.multiselect(
        "Existing skills or experience",
        [
            "caregiving",
            "cooking",
            "cleaning",
            "phone communication",
            "organization",
            "problem solving",
            "record keeping",
            "customer service",
            "email",
            "basic computer use"
        ],
        default=["caregiving", "cooking", "phone communication"]
    )
 
    additional_notes = st.text_area(
        "Case worker notes",
        placeholder=(
            "Example: Needs income soon, no car, prefers low-contact work, "
            "has caregiving experience. Do not include unnecessary sensitive details."
        )
    )
 
    if st.button("Run LLM Intake Agent + Generate Pathways"):
 
        profile = {
            "employment_history": employment_history,
            "education": education,
            "mobility": mobility,
            "income_timeline": income_timeline,
            "work_environment": work_environment,
            "night_shift": night_shift,
            "childcare": childcare,
            "documentation": documentation,
            "skills": skills,
            "additional_notes": additional_notes
        }
 
        st.session_state.case_profile = profile
        st.session_state.advocate_reviews = {}
        st.session_state.final_plan = None
 
        with st.spinner("Running privacy guardrail..."):
            privacy_warnings = privacy_guardrail(profile)
 
        with st.spinner("Running LLM Intake / Orchestrator Agent..."):
            intake = llm_intake_agent(profile, model_name)
 
        with st.spinner("Running rule-based safety + scoring agents..."):
            recs = career_scoring_agent(profile)
 
        with st.spinner("Running LLM Career Explanation Agent..."):
            career_explanation = llm_career_explanation_agent(profile, recs, model_name)
 
        for i, rec in enumerate(recs):
            with st.spinner(f"Running LLM Training Agent for {rec['title']}..."):
                rec["llm_training_plan"] = llm_training_agent(profile, rec, model_name)
 
        st.session_state.intake_summary = intake
        st.session_state.recommendations = recs
 
        st.success("Case analysis generated. Human advocate review is now required.")
 
    if st.session_state.case_profile:
 
        st.markdown("---")
        st.header("LLM Intake / Orchestrator Agent Output")
        st.write(st.session_state.intake_summary)
 
        st.header("Privacy Guardrail")
        for warning in privacy_guardrail(st.session_state.case_profile):
            st.write(f"• {warning}")
 
        st.header("Preliminary AI Recommendations")
        st.write("These are not final. They must be reviewed in the Human Advocate Review interface.")
 
        for idx, rec in enumerate(st.session_state.recommendations, start=1):
            with st.expander(f"{idx}. {rec['title']} — Risk: {rec['risk_level']}", expanded=True):
                colA, colB, colC = st.columns(3)
 
                with colA:
                    st.metric("Fit Score", rec["score"])
                    st.write(f"**Category:** {rec['category']}")
                    st.write(f"**Estimated wage:** {rec['estimated_wage']}")
 
                with colB:
                    st.write(f"**Training time:** {rec['training_time']}")
                    st.write(f"**Income speed:** {rec['income_speed']}")
                    st.write(f"**Long-term growth:** {rec['long_term_growth']}")
 
                with colC:
                    st.write(f"**Mobility need:** {rec['mobility_requirement']}")
                    st.write(f"**Contact level:** {rec['contact_level']}")
                    st.write(f"**Documentation need:** {rec['documentation_need']}")
 
                st.write("**Matched skills:**")
                if rec["matched_skills"]:
                    st.write(", ".join(rec["matched_skills"]))
                else:
                    st.write("No direct match detected.")
 
                st.write("**Safety flags:**")
                for flag in rec["safety_flags"]:
                    st.write(f"• {flag}")
 
                st.write("### LLM Training / Skill Recovery Agent")
                st.write(rec["llm_training_plan"])
 
        st.info("Next step: switch to Human Advocate Review in the sidebar.")
 
 
# ============================================================
# Interface 2: Human Advocate Review
# ============================================================
 
elif mode == "2. Human Advocate Review":
 
    st.header("Human Advocate Review Interface")
    st.write(
        "This interface is separate from the case worker intake. "
        "A human advocate reviews, modifies, rejects, or escalates AI-generated options."
    )
 
    if not st.session_state.case_profile or not st.session_state.recommendations:
        st.error("No case has been generated yet. Go to Case Worker Intake first.")
    else:
        st.subheader("Case Summary for Advocate")
        st.write(st.session_state.intake_summary)
 
        st.markdown("---")
        st.subheader("Review Each AI-Generated Pathway")
 
        for idx, rec in enumerate(st.session_state.recommendations, start=1):
            pathway_key = rec["title"]
 
            with st.expander(f"Review {idx}: {rec['title']} — AI risk level: {rec['risk_level']}", expanded=True):
                st.write("### AI-generated pathway")
                st.write(f"**Estimated wage:** {rec['estimated_wage']}")
                st.write(f"**Training time:** {rec['training_time']}")
                st.write(f"**Income speed:** {rec['income_speed']}")
                st.write(f"**Long-term growth:** {rec['long_term_growth']}")
 
                st.write("### Safety flags")
                for flag in rec["safety_flags"]:
                    st.write(f"• {flag}")
 
                st.write("### LLM Training Plan")
                st.write(rec["llm_training_plan"])
 
                decision = st.radio(
                    f"Advocate decision for {rec['title']}",
                    [
                        "Needs review",
                        "Approve for discussion",
                        "Modify",
                        "Reject as unsafe",
                        "Escalate"
                    ],
                    key=f"decision_{idx}"
                )
 
                note = st.text_area(
                    f"Advocate note for {rec['title']}",
                    placeholder=(
                        "Example: Good long-term option, but survivor needs immediate income. "
                        "Pair with faster short-term pathway."
                    ),
                    key=f"note_{idx}"
                )
 
                st.session_state.advocate_reviews[pathway_key] = {
                    "decision": decision,
                    "note": note
                }
 
        st.markdown("---")
 
        if st.button("Generate Final Plan Using Human Advocate Feedback"):
            with st.spinner("Running LLM Final Plan Agent with advocate feedback..."):
                final_plan = llm_final_plan_agent(
                    st.session_state.case_profile,
                    st.session_state.recommendations,
                    st.session_state.advocate_reviews,
                    model_name
                )
 
            st.session_state.final_plan = final_plan
            st.success("Final reviewed plan generated. Go to Final Reviewed Plan interface.")
 
        st.info(
            "This screen is the main human-in-the-loop checkpoint. "
            "The LLM cannot finalize a plan until advocate feedback is provided."
        )
 
 
# ============================================================
# Interface 3: Final Reviewed Plan
# ============================================================
 
elif mode == "3. Final Reviewed Plan":
 
    st.header("Final Reviewed Plan Interface")
 
    if not st.session_state.final_plan:
        st.error("No final reviewed plan yet. Go to Human Advocate Review and generate the final plan.")
    else:
        st.success("This plan incorporates human advocate feedback.")
        st.write(st.session_state.final_plan)
 
        st.markdown("---")
        st.subheader("Decision Record")
 
        st.write("### Human advocate decisions")
        st.json(st.session_state.advocate_reviews)
 
        st.write("### Timestamp")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
 
        st.warning(
            "Final decision remains with the survivor and trained human advocate. "
            "The AI output is only decision support."
        )
 
 
# ============================================================
# Interface 4: Architecture
# ============================================================
 
elif mode == "4. System Architecture":
 
    st.header("System Architecture")
 
    st.code(
        """
Case Worker Intake
        ↓
LLM Intake / Orchestrator Agent
        ↓
Rule-Based Privacy Guardrail
        ↓
Rule-Based Safety Guardrail
        ↓
Rule-Based Career Scoring Agent
        ↓
LLM Career Explanation Agent
        ↓
LLM Training / Skill Recovery Agent
        ↓
Separate Human Advocate Review Interface
        ↓
LLM Final Plan Agent using human feedback
        ↓
Final Reviewed Plan
        """,
        language="text"
    )
 
    st.subheader("Which agents are LLM-based?")
 
    st.write(
        """
**LLM-based agents**
- Intake / Orchestrator Agent
- Career Explanation Agent
- Training / Skill Recovery Agent
- Final Plan Agent using advocate feedback
 
**Rule-based agents**
- Privacy Guardrail
- Safety Guardrail
- Career Scoring
- Human review control logic
        """
    )
 
    st.subheader("Why hybrid?")
 
    st.write(
        """
The system uses LLMs for language understanding, explanation, and planning.
It uses rule-based guardrails for safety, privacy, scoring, and human control.
This keeps the system flexible while avoiding over-reliance on AI in a sensitive domain.
        """
    )
