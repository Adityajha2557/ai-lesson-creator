from modules.ai_client import ask_ai


def run_research_qc(lesson, research):
    sources = "\n".join(
        f"- {x.get('source_type')}: {x.get('title')} | {x.get('url')} | {x.get('snippet','')[:1000]}"
        for x in research
    ) or "No retrieved research sources were provided."

    prompt = f"""
Act as an independent research auditor. Do NOT rewrite the lesson.
Audit factual accuracy using only the supplied evidence and clearly distinguish:
- supported claims
- contradicted claims
- unsupported/unverifiable claims
- claims needing more recent or authoritative evidence
- source relevance and reliability
- missing context, ambiguity, or internal inconsistency

Do not treat an absence of evidence as proof that a claim is false.
Do not invent citations or pretend to have opened URLs.
For each issue provide: severity (High/Medium/Low), lesson claim or section,
evidence available, explanation, and a concrete suggested correction.
End with an overall verdict and a prioritized action list.

Keep the report concise and prioritize the most important issues.

LESSON:
{lesson}

RETRIEVED RESEARCH:
{sources}
"""

    # The user's Groq account reported a 1,000-token output ceiling.
    # Request 750 to leave headroom and reduce the chance of another HTTP 429.
    return ask_ai(prompt, max_tokens=750)
