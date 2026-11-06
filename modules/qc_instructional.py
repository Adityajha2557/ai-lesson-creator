from modules.ai_client import ask_ai

def run_instructional_qc(lesson, objective, title):
    prompt = f"""
Act as an independent instructional-design auditor. Do NOT assess factual truth;
that is handled by a separate research QC layer.
Evaluate this lesson against:
1. Explicit alignment to the learning objective
2. Clarity, sequencing, learner accessibility and terminology
3. Adequacy of explanations and worked examples
4. Relevance and feasibility of practical activity
5. Quality of knowledge checks and answer key
6. Timing: all content, activities and checks must fit within 45 minutes
7. Whether learners can demonstrate the stated objective by the end

For each issue provide severity (High/Medium/Low), section, why it matters,
and a specific improvement. Identify strengths too. End with an overall score
out of 10, verdict, and prioritized recommendations.
Do not invent content outside the lesson.

LESSON TITLE: {title}
LEARNING OBJECTIVE: {objective}

LESSON:
{lesson}
"""
    return ask_ai(prompt)
