
from modules.ai_client import ask_ai


def generate_lesson(title, objective, audience, level, research):

    # Prepare all research sources
    source_text = "\n".join(
        f"- [{x.get('source_type', 'Source')}] "
        f"Title: {x.get('title', 'Untitled')} | "
        f"URL: {x.get('url', '')} | "
        f"Details: {x.get('snippet', '')[:900]}"
        for x in research
        if x.get("url")
    ) or (
        "No external research results were available. "
        "Clearly label general knowledge and avoid fabricated citations."
    )

    # Extract YouTube videos separately
    youtube_videos = [
        x for x in research
        if x.get("source_type") == "YouTube" and x.get("url")
    ]

    if youtube_videos:

        youtube_text = "\n".join(
            f"- Title: {x.get('title', 'Untitled video')}\n"
            f"  URL: {x.get('url', '')}\n"
            f"  Details: {x.get('snippet', '')[:500]}"
            for x in youtube_videos
        )

    else:

        youtube_text = (
            "No YouTube videos were retrieved. "
            "Do not invent or recommend fabricated video links."
        )

    prompt = f"""
You are an experienced instructional designer and technical educator.

Create a self-contained lesson that can be completed in exactly
45 minutes or less.

LESSON TITLE: {title}
LEARNING OBJECTIVE: {objective}
AUDIENCE: {audience}
LEVEL: {level}

RESEARCH MATERIAL:
{source_text}

AVAILABLE YOUTUBE VIDEOS:
{youtube_text}

REQUIREMENTS:

1. Align every major section with the learning objective.

2. Use this timed plan, totaling 45 minutes:

   - 5 min: Learning outcomes and prerequisite activation
   - 10 min: Core concepts and explanations
   - 10 min: Worked examples / demonstrations
   - 10 min: Guided practical activity
   - 5 min: Knowledge check (include answers separately)
   - 5 min: Recap and application

3. Explain terminology in accessible language.

4. Include accurate examples and practical applications.

5. Include 3-5 knowledge-check questions with an answer key
   and brief explanations.

6. Add a dedicated section titled:
   "Supplementary YouTube Videos"

   - Include only videos supplied in AVAILABLE YOUTUBE VIDEOS.
   - Include the exact video title and URL.
   - Include channel or publication information only if supplied.
   - Briefly explain how each video supports the lesson.
   - Do not fabricate video titles, channels, URLs, or details.
   - If no videos are available, explicitly state that no
     supplementary YouTube videos were retrieved.

7. Add a References section with source title, source type,
   and exact URL. Never invent sources.

8. Distinguish verified source-backed facts from general
   explanations where needed.

9. Do not claim the lesson is validated; it will be checked
   separately through independent quality-control layers.

10. Output clean Markdown. Be detailed enough to teach from,
    but respect the 45-minute limit.

11. Ensure the lesson is practical, engaging, logically
    structured, and suitable for the specified audience.
"""

    return ask_ai(prompt)
