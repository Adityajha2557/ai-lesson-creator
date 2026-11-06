# AI Lesson Creator

A local Streamlit application that researches and generates 45-minute lessons, runs two independent QC audits, supports instructor editing/saving, and exports lesson materials.

## Features
- Lesson title and learning objective inputs
- Website research through Tavily (optional API key)
- Book metadata through Google Books API
- YouTube video search through YouTube Data API (optional API key)
- Gemini-powered lesson generation
- Independent research/factual QC and instructional QC
- Instructor editing, SQLite saving, preview and DOCX/PDF export
- Basic input validation and retryable steps

## Setup

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your Gemini API key.
5. Add Tavily and YouTube API keys to enable those research integrations.
6. Run:

   ```bash
   streamlit run app.py
   ```

## API keys
- Gemini: required for generation and QC.
- Tavily: optional web search.
- YouTube Data API: optional video search.
- Google Books API: public endpoint; no key required for basic queries.

Never commit `.env` or API keys to GitHub.

## Important limitations of this MVP
- LLM-based QC is an audit assistant, not a formal proof of truth. Review high-severity findings manually.
- Research availability depends on configured APIs and network access.
- The PDF export currently prioritizes text and headings; advanced Markdown formatting can be improved.
- Save creates a new versioned database record rather than overwriting an earlier record, preserving prior work.

## Test cases
1. HTTP Requests and Responses — Explain GET and POST methods and distinguish between 2xx, 4xx and 5xx response status categories.
2. SQL Joins — Explain INNER JOIN, LEFT JOIN, RIGHT JOIN and FULL OUTER JOIN using practical examples.
