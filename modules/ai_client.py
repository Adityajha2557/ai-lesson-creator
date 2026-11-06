"""AI client with automatic Gemini -> Groq failover.

Gemini is the primary provider. If Gemini fails, Groq is used as a fallback.
The Groq output-token cap is configurable because some accounts have a
per-request output-token limit lower than the model's maximum completion size.
"""
import logging
import os

import requests

logger = logging.getLogger(__name__)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _ask_gemini(prompt: str) -> str:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    response = client.models.generate_content(model=model, contents=prompt)
    result = getattr(response, "text", None)

    if not result:
        raise RuntimeError("Gemini returned an empty response.")

    return result.strip()


def _ask_groq(prompt: str, max_tokens: int = 900) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add a Groq API key to .env "
            "to enable the automatic fallback."
        )

    # These are current Groq model IDs. Availability can vary by account.
    configured = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    backup_models = os.getenv(
        "GROQ_BACKUP_MODELS", "openai/gpt-oss-20b"
    )
    models = [configured.strip()] + [
        item.strip() for item in backup_models.split(",") if item.strip()
    ]

    # Respect the low output-token ceiling reported by this user's Groq account.
    # A small safety margin below 1,000 helps avoid another 429 response.
    try:
        max_tokens = int(max_tokens)
    except (TypeError, ValueError):
        max_tokens = 900
    max_tokens = max(100, min(max_tokens, 900))

    errors = []

    for model in dict.fromkeys(models):
        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a careful educational content and "
                                "research assistant. Follow instructions precisely. "
                                "Do not invent sources or facts."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                    "max_completion_tokens": max_tokens,
                },
                timeout=90,
            )

            if not response.ok:
                try:
                    detail = response.json().get("error", {}).get(
                        "message", response.text[:500]
                    )
                except ValueError:
                    detail = response.text[:500]
                raise RuntimeError(f"HTTP {response.status_code}: {detail}")

            data = response.json()
            result = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )

            if not result:
                raise RuntimeError("Groq returned an empty response.")

            logger.info("AI response generated using Groq model %s.", model)
            return result.strip()

        except Exception as exc:
            logger.warning("Groq model %s failed: %s", model, exc)
            errors.append(f"{model}: {exc}")

    raise RuntimeError("All configured Groq models failed. " + " | ".join(errors))


def ask_ai(prompt: str, max_tokens: int = 900) -> str:
    """Use Gemini first, then Groq if Gemini fails.

    max_tokens applies to Groq only. Existing calls that pass just `prompt`
    continue to work.
    """
    preferred = os.getenv("AI_PROVIDER", "gemini").strip().lower()

    if preferred == "groq":
        return _ask_groq(prompt, max_tokens=max_tokens)

    try:
        return _ask_gemini(prompt)
    except Exception as gemini_error:
        logger.warning(
            "Gemini request failed; attempting Groq fallback: %s",
            gemini_error,
        )
        try:
            result = _ask_groq(prompt, max_tokens=max_tokens)
            logger.info("Gemini unavailable; Groq fallback succeeded.")
            return result
        except Exception as groq_error:
            raise RuntimeError(
                f"Gemini failed: {gemini_error}\n"
                f"Groq fallback also failed: {groq_error}"
            ) from groq_error
