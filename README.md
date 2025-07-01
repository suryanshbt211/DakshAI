# DakshAI

#   Multi-Agentic Policy-Guided AI Educational Assistant

**DakshAI** is a multi-agentic, AI-powered educational assistant that automates the generation of syllabi, assessments, and peer-reviewed student evaluations—strictly aligned with institutional, governmental, and quality assurance policies. It streamlines curriculum planning, question design, and grading using intelligent agents coordinated through a LangGraph-powered orchestration pipeline.

![Screenshot (55)](https://github.com/user-attachments/assets/e12208d1-78e8-4cf1-a412-c21bf23254b4)


---

##  Key Features

-  **Policy-Driven Automation**: Extracts institutional guidelines from PDFs or text and converts them into structured academic rules.
-  **Syllabus Generation**: Produces weekly syllabi aligned with learning goals, policy rules, and learning analytics principles.
-  **Assessment Authoring**: Generates Bloom’s taxonomy-aligned questions tailored to course content and compliance guidelines.
-  **Multi-Agent Peer Evaluation**: Simulates 6 AI peer reviewers, each focusing on different rubric dimensions (e.g., grammar, reasoning, creativity).
-  **Rubric-Based Grading**: Uses a 20-point scoring framework customizable to institutional standards.
-  **Interactive Streamlit UI**: Full user interface for uploading policies, customizing content, and triggering peer evaluation.
-  **LangGraph Orchestration**: Ensures agent workflows are executed in a controlled, deterministic, and transparent pipeline.

---

##  Multi-Agent Architecture

DakshAI uses **9 autonomous agents**, with tasks distributed as follows:

###  Academic Design Agents
| Agent | Function |
|-------|----------|
| 1. Policy Parser Agent | Extracts rules for design, assessment, conduct, and analytics from institutional policies |
| 2. Syllabus Generator Agent | Designs a weekly syllabus table aligned with policy constraints and learning goals |
| 3. Question Generator Agent | Produces assessments aligned with Bloom’s Taxonomy, outcomes, and assessment policy |

###  Peer Reviewer Agents
| Agent | Specialization |
|--------|----------------|
| 4. Peer Reviewer #1 | Conceptual Accuracy and Depth |
| 5. Peer Reviewer #2 | Grammar, Clarity, Communication |
| 6. Peer Reviewer #3 | Rubric and Policy Compliance |
| 7. Peer Reviewer #4 | Critical Thinking and Reasoning |
| 8. Peer Reviewer #5 | Creativity and Problem Solving |
| 9. Peer Reviewer #6 | Growth Mindset and Student Development |

Each reviewer uses a shared rubric but evaluates from a different lens to ensure **multi-perspective grading**.

---

##  Folder & Code Structure

```bash
.
├── DakshAI.py                # Main application file (Streamlit UI + backend)
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation (this file)
└── assets/                   # (Optional) Store PDFs, images, or sample rubrics
🛠️ How It Works
Upload or Paste Policy: Input an academic policy PDF or text document.

Set Course Metadata: Title, domain, level (UG/PG), and learning goals.

Run Syllabus Generator: Extract rules and generate the policy-compliant syllabus.

Generate Questions: Auto-create a table of assessment questions per Bloom’s level.

Enter Student Answer: Paste a student answer to any generated question.

Run Peer Review: Simulate 6 AI peer reviewers and compute average score.

Review Results: Get full feedback, individual scores, and improvement tips.
