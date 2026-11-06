from modules.ai_client import ask_ai

def generate_lesson(title, objective, audience, level, research):
    source_text = "\n".join(
        f"- [{x.get('source_type')}] {x.get('title')} | {x.get('url')} | {x.get('snippet','')[:900]}"
        for x in research if x.get("url")
    ) or "No external research results were available. Clearly label general knowledge and avoid fabricated citations."

    prompt = f"""
You are an experienced instructional designer and technical educator.
Create a self-contained lesson that can be completed in exactly 45 minutes or less.

LESSON TITLE: {title}
LEARNING OBJECTIVE: {objective}
AUDIENCE: {audience}
LEVEL: {level}

RESEARCH MATERIAL:
{source_text}

Requirements:
1. Align every major section to the learning objective.
2. Use this timed plan, totaling 45 minutes:
   - 5 min: learning outcomes and prerequisite activation
   - 10 min: core concepts and explanations
   - 10 min: worked examples / demonstrations
   - 10 min: guided practical activity
   - 5 min: knowledge check (include answers separately)
   - 5 min: recap and application
3. Explain terminology in accessible language.
4. Include accurate examples and practical applications.
5. Include 3-5 knowledge-check questions with answer key and brief explanations.
6. Include relevant supplementary YouTube videos only if present in the research material.
7. Add a References section with source title, source type, and exact URL. Never invent sources.
8. Distinguish verified source-backed facts from general explanation where needed.
9. Do not claim the lesson is validated; it will be checked separately.
10. Output clean Markdown. Be detailed enough to teach from, but respect the 45-minute limit.
"""
    return ask_ai(prompt)
