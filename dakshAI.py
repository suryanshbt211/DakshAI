import os
import streamlit as st
from typing import TypedDict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import re

# --- Setup API Key for Gemini ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyCf4zhRvpmANps5SVaIPOZ3QoZnHA5SNlw"

# --- LLM ---
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# --- Hardcoded Rubric  ---
HARDCODED_RUBRIC = """
Score Criteria (out of 20):
- Application / Presentation of Concept: 2 marks
- Detailing and Understanding: 1 mark
- Skills Exploration: 1 mark
- Basics of Design Principles: 1 mark
- Research and Comprehension: 2 marks
- Meta-cognition and Critical Thinking: 1.5 marks
- Perception, Observation, and Sensitivity: 1.5 marks
- Conceptual Clarity and Comprehension (Theory): 2 marks
- Reflective Thinking: 1.5 marks
- Communication: 0.75 marks
- Conceptual Clarity: 2 marks
- Exploration and Improvisation: 1.5 marks
- Problem-solving and Lateral Thinking: 1.5 marks
- Originality and Visualization: 1 mark

Guidelines:
- Provide justification for each score.
- Consider understanding, clarity, exploration, critical thinking, originality.
"""

# --- State Definition ---
class AutoTeachState(TypedDict):
    policy: Optional[str]
    parsed_policy: Optional[str]
    syllabus: Optional[str]
    questions: Optional[str]
    evaluation: Optional[str]
    feedback: Optional[str]
    level: Optional[str]
    title: Optional[str]
    domain: Optional[str]
    goals: Optional[str]
    question: Optional[str]
    answer: Optional[str]
    rubric: Optional[str]

# --- Nodes ---
def parse_policy_node(state):
    prompt = f"""
You are an academic policy parser specialized in education policies.
Parse the following institutional policy strictly into:
- Course Design Rules
- Assessment Rules
- Conduct Rules
- Learning Analytics Guidelines

Policy:
{state['policy']}
"""
    return {"parsed_policy": gemini_llm.invoke(prompt).content}

def generate_syllabus_node(state):
    prompt = f"""
Using the parsed policy below, design a detailed syllabus for a {state['level']} course titled '{state['title']}' in the domain {state['domain']}.
Learning goals: {state['goals']}

Parsed Policy:
{state['parsed_policy']}

Requirements:
- Provide a markdown table: Week, Topic, Learning Outcomes, Activities, Assessments, Policy Alignment
- Ensure all course content strictly follows the policy rules
- Include adaptive learning recommendations and use learning analytics where applicable
"""
    return {"syllabus": gemini_llm.invoke(prompt).content}

def generate_questions_node(state):
    prompt = f"""
Based on the following syllabus and parsed policy, generate assessment questions aligned with the policy:

Syllabus:
{state['syllabus']}

Parsed Policy:
{state['parsed_policy']}

Generate a markdown table with columns:
Question | Type (MCQ, Essay, Short) | Week | Bloom's Level | Learning Outcome | Policy Criterion

Ensure questions reflect policy's assessment rules.
"""
    return {"questions": gemini_llm.invoke(prompt).content}

# --- Graph 1: Syllabus and Questions ---
syllabus_graph = StateGraph(AutoTeachState)
syllabus_graph.set_entry_point("ParsePolicy")
syllabus_graph.add_node("ParsePolicy", RunnableLambda(parse_policy_node))
syllabus_graph.add_node("GenerateSyllabus", RunnableLambda(generate_syllabus_node))
syllabus_graph.add_node("GenerateQuestions", RunnableLambda(generate_questions_node))
syllabus_graph.add_edge("ParsePolicy", "GenerateSyllabus")
syllabus_graph.add_edge("GenerateSyllabus", "GenerateQuestions")
syllabus_graph.add_edge("GenerateQuestions", END)
syllabus_chain = syllabus_graph.compile()

# --- Peer Evaluation Helpers ---

# Shared prompt context for all peers
def generic_context_and_instructions(state):
    return f"""
### Institutional Policy:
{state.get('parsed_policy', 'No policy provided')}

### Question:
{state['question']}

### Student Answer:
{state['answer']}

### Rubric:
{state['rubric']}

Instructions:
1. Score the answer on a 20-point scale.
2. Justify the score thoroughly using rubric criteria and relevant policy rules.
3. Provide detailed feedback on:
   - Accuracy
   - Clarity
   - Policy compliance
   - Strengths and weaknesses
   - Recommendations for improvement

Be strict and insightful. Provide the final score clearly like: Final Score: XX/20
"""

# 6 specialized peer roles
def evaluate_answer_prompt_peer1(state):
    return f"""
You are Peer Reviewer #1: An evaluator focused on **conceptual accuracy and depth**.

Your job:
- Check for factual correctness and logic
- Judge conceptual depth and understanding

{generic_context_and_instructions(state)}
"""

def evaluate_answer_prompt_peer2(state):
    return f"""
You are Peer Reviewer #2: An evaluator focused on **grammar, clarity, communication**, and **organization**.

Your job:
- Judge the **grammatical accuracy** of the answer.
- Assess sentence structure, punctuation, and proper academic expression.
- Check coherence, logical flow, and clarity of ideas.
- Highlight areas where grammar or clarity impacts understanding.

You may point out specific grammar mistakes or suggest improved phrasing.

{generic_context_and_instructions(state)}
"""


def evaluate_answer_prompt_peer3(state):
    return f"""
You are Peer Reviewer #3: A **rubric and institutional policy compliance** evaluator.

Your job:
- Enforce policy and rubric strictly
- Penalize deviation from expected formats or standards

{generic_context_and_instructions(state)}
"""

def evaluate_answer_prompt_peer4(state):
    return f"""
You are Peer Reviewer #4: A **critical thinking and reasoning** specialist.

Your job:
- Evaluate originality of thought
- Look for logical analysis and reasoning quality

{generic_context_and_instructions(state)}
"""

def evaluate_answer_prompt_peer5(state):
    return f"""
You are Peer Reviewer #5: A **creativity, visualization, and problem-solving** analyst.

Your job:
- Reward lateral thinking and creative approach
- Look for use of analogies or unique ideas

{generic_context_and_instructions(state)}
"""

def evaluate_answer_prompt_peer6(state):
    return f"""
You are Peer Reviewer #6: A **student development and growth mindset** advocate.

Your job:
- Provide constructive, motivating feedback
- Evaluate learning mindset and progress orientation

{generic_context_and_instructions(state)}
"""

# Dispatcher function for peer-specific prompts
PEER_PROMPT_FUNCTIONS = [
    evaluate_answer_prompt_peer1,
    evaluate_answer_prompt_peer2,
    evaluate_answer_prompt_peer3,
    evaluate_answer_prompt_peer4,
    evaluate_answer_prompt_peer5,
    evaluate_answer_prompt_peer6
]

# Call the correct peer prompt
def evaluate_single_peer(state, peer_id=1):
    prompt_func = PEER_PROMPT_FUNCTIONS[peer_id - 1]
    prompt = prompt_func(state)
    try:
        response = gemini_llm.invoke(prompt).content
        return response
    except Exception as e:
        return f"Peer Reviewer #{peer_id} failed to respond. Final Score: 0/20\nError: {e}"

# Simulate all peers and compute aggregate
def peer_assessment_simulation(state, num_peers=6):
    peer_evaluations = []
    scores = []

    for i in range(1, num_peers + 1):
        evaluation_text = evaluate_single_peer(state, peer_id=i)
        peer_evaluations.append((i, evaluation_text))

        match = re.search(r"(?i)\b(?:final\s*)?score\s*[:\-]?\s*(\d+(\.\d+)?)(?:\s*/20|\s*\/20)?", evaluation_text, re.IGNORECASE)

        if match:
            scores.append(float(match.group(1)))
        else:
            scores.append(0)

    avg_score = sum(scores) / len(scores) if scores else 0

    combined_feedback = "\n\n".join(
        [f"**Peer Reviewer #{peer_id}:**\n{eval_text}" for peer_id, eval_text in peer_evaluations]
    )

    return {
        "peer_reviews": combined_feedback,
        "average_score": avg_score,
        "scores": scores,
    }

# --- Streamlit UI ---
st.set_page_config(page_title="DakshAI", layout="wide")
st.markdown("<h1 style='text-align:center;'> DakshAI– Policy-Guided AI Teaching Assistant with Peer Assessment</h1>", unsafe_allow_html=True)

# Step 1: Syllabus Generation
# st.markdown("## Step 1: Enter Institutional Policy & Course Info")

import fitz  # PyMuPDF for extracting text from PDFs

st.markdown("## Step 1: Enter Institutional Policy & Course Info")

# Option to upload a policy PDF
uploaded_pdf = st.file_uploader("Upload Institutional Policy (PDF)", type=["pdf"])

# Extract text from PDF if uploaded
extracted_policy_text = ""
if uploaded_pdf:
    with st.spinner("Extracting text from uploaded PDF..."):
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        extracted_policy_text = "\n".join([page.get_text() for page in doc])

# Manual policy entry (fallback or editable override)
policy = st.text_area(
    "Institutional Policy (you can edit if uploaded)",
    value=extracted_policy_text if extracted_policy_text else "",
    height=200
)

title = st.text_input("Course Title", value="Introduction to AI")
domain = st.text_input("Domain", value="Computer Science")
goals = st.text_area("Learning Goals", value="Understand core AI principles and applications.", height=80)
level = st.selectbox("Level", ["Undergraduate", "Postgraduate"])

if st.button("Generate Syllabus & Questions"):
    inputs = {
        "policy": policy,
        "title": title,
        "domain": domain,
        "goals": goals,
        "level": level
    }
    with st.spinner("Generating syllabus and questions..."):
        result = syllabus_chain.invoke(inputs)

    if "parsed_policy" in result:
        st.subheader("Parsed Policy")
        st.text_area("Parsed Policy", value=result["parsed_policy"], height=150)
        st.session_state["parsed_policy"] = result["parsed_policy"]

    if "syllabus" in result:
        st.subheader("Generated Syllabus")
        st.markdown(result["syllabus"], unsafe_allow_html=True)

    if "questions" in result:
        st.subheader("Generated Questions")
        st.markdown(result["questions"], unsafe_allow_html=True)


# Step 2: Student Evaluation with Peer Assessment
st.markdown("---")
st.markdown("## Step 2: Student Evaluation with Peer Assessment Simulation")

eval_question = st.text_area("Question", height=80)
eval_answer = st.text_area("Student Answer", height=150)

st.markdown("**6 Peer Review Agents**")

if st.button("Evaluate Student Answer with Peer Assessment"):
    parsed_policy = st.session_state.get("parsed_policy", "")
    eval_inputs = {
        "question": eval_question,
        "answer": eval_answer,
        "rubric": HARDCODED_RUBRIC,
        "parsed_policy": parsed_policy
    }

    with st.spinner("Running peer assessment..."):
        peer_results = peer_assessment_simulation(eval_inputs, num_peers=6)

    import re
    import pandas as pd

# Extract individual peer reviews as a list (split combined_feedback)
    peer_texts = []
    scores = []
    for i in range(1, 7):
        # Find the feedback for each reviewer
        match = re.search(
            fr"\*\*Peer Reviewer #{i}:\*\*\n(.+?)(?=(\*\*Peer Reviewer #\d+:\*\*|$))",
            peer_results["peer_reviews"],
            flags=re.DOTALL,
        )
        feedback = match.group(1).strip() if match else "No feedback."
        peer_texts.append(feedback)
    
        # Extract the score from the review text (assumes score is in format "Score: X/20" or "Final Score: X/20")
        score_match = re.search(r"(?i)(?:final\s*)?score\s*[:\-]?\s*(\d+(\.\d+)?)/20", feedback)
        if score_match:
            scores.append(float(score_match.group(1)))  # Extract the score
        else:
            scores.append(0)  # Default to 0 if no score is found
    
    avg = sum(scores) / len(scores) if scores else 0
    
    # Score Table
    score_data = {
        "Peer Reviewer": [f"#{i}" for i in range(1, 7)] + ["Average"],
        "Score": [f"{float(s):.2f}" for s in scores] + [f"{float(avg):.2f} / 20"]
    }
    st.subheader("Peer Reviewer Scores")
    st.table(pd.DataFrame(score_data))
    
    # Final Verdict (you can customize)
    st.markdown("🏁 **Final Verdict:**")
    st.markdown(f"### FINAL SCORE AWARDED: {avg:.2f} / 20")
 

    
   

    # Expandable Dropdowns for Reviews
    st.subheader("Peer Review Details")
    for i, text in enumerate(peer_texts, start=1):
        with st.expander(f"Peer Reviewer #{i} Feedback", expanded=False):
            st.markdown(text)
# # Step 2: Student Evaluation with Peer Assessment
# st.markdown("---")
# st.markdown("## Step 2: Student Evaluation with Peer Assessment Simulation")

# eval_question = st.text_area("Question", height=80)
# eval_answer = st.text_area("Student Answer", height=150)

# st.markdown("**6 Peer review agents**")

# if st.button("Evaluate Student Answer with Peer Assessment"):
#     parsed_policy = st.session_state.get("parsed_policy", "")
#     eval_inputs = {
#         "question": eval_question,
#         "answer": eval_answer,
#         "rubric": HARDCODED_RUBRIC,
#         "parsed_policy": parsed_policy
#     }
#     with st.spinner("Running peer assessment..."):
#         peer_results = peer_assessment_simulation(eval_inputs, num_peers=6)

#     st.subheader("Individual Peer Reviews & Scores")
#     st.markdown(peer_results["peer_reviews"], unsafe_allow_html=True)

#     st.subheader(f"Average Score: {peer_results['average_score']:.2f} / 20")
#     st.markdown(f"Scores from each peer reviewer: {peer_results['scores']}")
