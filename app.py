
import streamlit as st
from dotenv import load_dotenv

from modules.database import (
    init_db,
    save_project,
    list_projects,
    load_project
)
from modules.research import collect_research
from modules.lesson_generator import generate_lesson
from modules.qc_research import run_research_qc
from modules.qc_instructional import run_instructional_qc
from modules.export import export_docx, export_pdf


# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Lesson Creator",
    page_icon="📚",
    layout="wide"
)

init_db()

st.title("📚 AI Lesson Creator")
st.caption(
    "Research-backed, quality-checked lessons designed "
    "for a 45-minute learning experience."
)


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

defaults = {
    "lesson": "",
    "research": [],
    "research_qc": "",
    "instructional_qc": "",
    "title": "",
    "objective": "",
    "project_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# SIDEBAR - SAVED PROJECTS
# --------------------------------------------------

with st.sidebar:
    st.header("Workspace")

    saved = list_projects()

    options = ["Create a new lesson"] + [
        f'{p["id"]} · {p["title"]}'
        for p in saved
    ]

    selected = st.selectbox("Saved lessons", options)

    if selected == "Create a new lesson":
        if st.session_state.get("selected_project") is not None:
            st.session_state["selected_project"] = None
            st.session_state["project_id"] = None
            st.session_state["title"] = ""
            st.session_state["objective"] = ""
            st.session_state["lesson"] = ""
            st.session_state["research"] = []
            st.session_state["research_qc"] = ""
            st.session_state["instructional_qc"] = ""

    else:
        project_id = int(selected.split(" · ")[0])

        if st.session_state.get("selected_project") != project_id:
            project = load_project(project_id)

            if project:
                st.session_state["selected_project"] = project_id
                st.session_state["project"] = project
                st.session_state["project_id"] = project_id
                st.session_state["title"] = project["title"]
                st.session_state["objective"] = project["objective"]
                st.session_state["lesson"] = project["lesson"]
                st.session_state["research"] = project["research"]
                st.session_state["research_qc"] = project["research_qc"]
                st.session_state["instructional_qc"] = project["instructional_qc"]

    st.divider()

    st.caption("API keys are configured locally in your .env file.")


# --------------------------------------------------
# APPLICATION TABS
# --------------------------------------------------

tab_generate, tab_review, tab_qc, tab_export = st.tabs(
    [
        "1 · Generate",
        "2 · Review & edit",
        "3 · Quality control",
        "4 · Export"
    ]
)


# ==================================================
# TAB 1 - GENERATE LESSON AND RESEARCH
# ==================================================

with tab_generate:

    st.subheader("Create a lesson")

    title = st.text_input(
        "Lesson title",
        value=st.session_state.get("title", "")
    )

    objective = st.text_area(
        "Learning objective",
        value=st.session_state.get("objective", ""),
        placeholder="By the end of this lesson, learners will be able to..."
    )

    col1, col2 = st.columns(2)

    with col1:
        audience = st.text_input(
            "Target audience",
            value="Beginner-level learners"
        )

    with col2:
        level = st.selectbox(
            "Difficulty",
            ["Beginner", "Intermediate", "Advanced"]
        )

    if st.button(
        "🔎 Research and generate lesson",
        type="primary",
        use_container_width=True
    ):

        if not title.strip() or not objective.strip():
            st.error(
                "Please enter both a lesson title and a learning objective."
            )

        else:

            st.session_state.title = title
            st.session_state.objective = objective

            st.session_state.lesson = ""
            st.session_state.research_qc = ""
            st.session_state.instructional_qc = ""

            try:

                with st.status(
                    "Researching sources...",
                    expanded=True
                ) as status:

                    research = collect_research(title, objective)

                    st.session_state.research = research

                    st.write(
                        f"Collected {len(research)} research items."
                    )

                    st.write(
                        "Generating a structured 45-minute lesson..."
                    )

                    lesson = generate_lesson(
                        title,
                        objective,
                        audience,
                        level,
                        research
                    )

                    st.session_state.lesson = lesson

                    status.update(
                        label="Lesson generated successfully",
                        state="complete"
                    )

                st.success(
                    "Your lesson is ready. Review it and run both QC layers."
                )

            except Exception as e:

                st.error(f"Generation failed: {e}")

                st.info(
                    "Your previously saved projects are preserved. "
                    "Check API keys and retry."
                )


    # --------------------------------------------------
    # RESEARCH SOURCES DISPLAY
    # --------------------------------------------------

    if st.session_state.research:

        st.markdown("#### Research sources")

        youtube_videos = [
            x for x in st.session_state.research
            if x.get("source_type") == "YouTube"
        ]

        books = [
            x for x in st.session_state.research
            if x.get("source_type") == "Book"
        ]

        websites = [
            x for x in st.session_state.research
            if x.get("source_type") == "Website"
        ]

        st.write(
            f"Websites: {len(websites)} | "
            f"Books: {len(books)} | "
            f"YouTube videos: {len(youtube_videos)}"
        )

        # Display all research items
        for item in st.session_state.research:

            source_type = item.get("source_type", "Source")
            title = item.get("title", "Untitled")
            url = item.get("url", "")

            # Research warnings
            if source_type == "Research warning":

                st.warning(
                    f'{title}: {item.get("snippet", "")}'
                )

            # YouTube videos
            elif source_type == "YouTube":
                with st.container(border=True):
                    st.markdown(f"**▶ {title}**")
                    st.caption(item.get("snippet", ""))

                    if url:
                        video_id = url.split("v=")[-1].split("&")[0]
                        st.components.v1.iframe(
                            f"https://www.youtube-nocookie.com/embed/{video_id}",
                            height=315,
                            scrolling=False
                        )
                        st.markdown(f"[Watch on YouTube]({url})")

            # Websites and books
            else:
                if url:
                    st.markdown(
                        f'- **{source_type}** — [{title}]({url})'
                    )
                else:
                    st.markdown(
                        f'- **{source_type}** — {title}'
                    )

                if item.get("snippet"):
                    st.caption(item["snippet"][:350])


# ==================================================
# TAB 2 - INSTRUCTOR REVIEW AND EDITING
# ==================================================

with tab_review:

    st.subheader("Instructor review")

    if st.session_state.lesson:

        edited = st.text_area(
            "Edit lesson content (Markdown supported)",
            value=st.session_state.lesson,
            height=650
        )

        st.session_state.lesson = edited

        if st.button(
            "💾 Save lesson",
            type="primary"
        ):

            try:

                pid = save_project(
                    st.session_state.get("title", "Untitled lesson"),
                    st.session_state.get("objective", ""),
                    st.session_state.lesson,
                    st.session_state.research,
                    st.session_state.research_qc,
                    st.session_state.instructional_qc
                )

                st.session_state.project_id = pid

                st.session_state.selected_project = pid

                st.success(f"Saved lesson #{pid}.")

            except Exception as e:

                st.error(f"Could not save lesson: {e}")

        with st.expander("Preview lesson"):

            st.markdown(st.session_state.lesson)

    else:

        st.info("Generate or load a lesson to review it.")


# ==================================================
# TAB 3 - QUALITY CONTROL
# ==================================================

with tab_qc:

    st.subheader("Independent quality-control layers")

    if not st.session_state.lesson:

        st.info("Generate or load a lesson first.")

    else:

        c1, c2 = st.columns(2)

        # Research QC
        with c1:

            if st.button(
                "Run Research & Factual Accuracy QC",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Checking claims against research sources..."
                    ):

                        st.session_state.research_qc = run_research_qc(
                            st.session_state.lesson,
                            st.session_state.research
                        )

                except Exception as e:

                    st.error(f"Research QC failed: {e}")

        # Instructional QC
        with c2:

            if st.button(
                "Run Instructional Quality QC",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Evaluating instructional design..."
                    ):

                        st.session_state.instructional_qc = (
                            run_instructional_qc(
                                st.session_state.lesson,
                                st.session_state.get("objective", ""),
                                st.session_state.get("title", "")
                            )
                        )

                except Exception as e:

                    st.error(f"Instructional QC failed: {e}")


        # Display Research QC
        if st.session_state.research_qc:

            st.markdown(
                "### QC Layer 1 — Research and factual accuracy"
            )

            st.markdown(
                st.session_state.research_qc
            )


        # Display Instructional QC
        if st.session_state.instructional_qc:

            st.markdown(
                "### QC Layer 2 — Instructional quality"
            )

            st.markdown(
                st.session_state.instructional_qc
            )


# ==================================================
# TAB 4 - EXPORT
# ==================================================

with tab_export:

    st.subheader("Export finalized lesson")

    if not st.session_state.lesson:

        st.info("Generate or load a lesson first.")

    else:

        st.markdown(
            "Export includes the lesson, references, "
            "and available QC reports."
        )

        col1, col2 = st.columns(2)

        # DOCX EXPORT
        with col1:

            if st.button(
                "Prepare DOCX",
                use_container_width=True
            ):

                try:

                    path = export_docx(
                        st.session_state.get("title", "lesson"),
                        st.session_state.lesson,
                        st.session_state.research,
                        st.session_state.research_qc,
                        st.session_state.instructional_qc
                    )

                    with open(path, "rb") as f:

                        st.download_button(
                            "⬇️ Download DOCX",
                            f,
                            file_name="lesson.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                except Exception as e:

                    st.error(f"DOCX export failed: {e}")


        # PDF EXPORT
        with col2:

            if st.button(
                "Prepare PDF",
                use_container_width=True
            ):

                try:

                    path = export_pdf(
                        st.session_state.get("title", "lesson"),
                        st.session_state.lesson,
                        st.session_state.research,
                        st.session_state.research_qc,
                        st.session_state.instructional_qc
                    )

                    with open(path, "rb") as f:

                        st.download_button(
                            "⬇️ Download PDF",
                            f,
                            file_name="lesson.pdf",
                            mime="application/pdf"
                        )

                except Exception as e:

                    st.error(f"PDF export failed: {e}")
