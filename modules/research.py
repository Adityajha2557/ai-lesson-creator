
import os
import time
import requests


def make_request(url, params=None, json_data=None, headers=None, timeout=25):
    """
    Make an HTTP request with retries for rate limits
    and temporary server errors.
    """

    for attempt in range(3):
        try:
            if json_data is not None:
                response = requests.post(
                    url,
                    json=json_data,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )

            if response.status_code in (429, 500, 502, 503, 504):

                if attempt < 2:
                    retry_after = response.headers.get("Retry-After")

                    try:
                        delay = min(float(retry_after), 15) if retry_after else 2 ** (attempt + 1)
                    except ValueError:
                        delay = 2 ** (attempt + 1)

                    time.sleep(delay)
                    continue

            response.raise_for_status()
            return response

        except requests.RequestException:
            if attempt == 2:
                raise

            time.sleep(2 ** (attempt + 1))

    return None


def collect_research(title: str, objective: str):
    """Collect website, book and YouTube research."""

    results = []
    query = f"{title} {objective}"

    # --------------------------------------------------
    # 1. WEBSITE RESEARCH - TAVILY
    # --------------------------------------------------

    tavily_key = os.getenv("TAVILY_API_KEY")

    if tavily_key:

        try:
            response = make_request(
                "https://api.tavily.com/search",
                json_data={
                    "api_key": tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 5,
                    "include_answer": False
                },
                timeout=25
            )

            for item in response.json().get("results", []):

                if not item.get("url"):
                    continue

                results.append({
                    "source_type": "Website",
                    "title": item.get("title", "Web result"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")
                })

        except requests.RequestException as exc:

            results.append({
                "source_type": "Research warning",
                "title": "Web search unavailable",
                "url": "",
                "snippet": str(exc)
            })

    else:

        results.append({
            "source_type": "Research warning",
            "title": "Website search API key missing",
            "url": "",
            "snippet": "Add TAVILY_API_KEY to your .env file."
        })

    # --------------------------------------------------
    # 2. BOOK RESEARCH - GOOGLE BOOKS
    # --------------------------------------------------

    books_key = (
    os.getenv("GOOGLE_BOOKS_API_KEY")
    or os.getenv("YOUTUBE_API_KEY")
)

    book_params = {
        "q": title,
        "maxResults": 5,
        "printType": "books"
    }

    if books_key:
        book_params["key"] = books_key

    try:

        response = make_request(
            "https://www.googleapis.com/books/v1/volumes",
            params=book_params,
            timeout=20
        )

        book_items = response.json().get("items", [])

        for item in book_items:

            info = item.get("volumeInfo", {})

            results.append({
                "source_type": "Book",
                "title": info.get("title", "Book"),
                "url": info.get("infoLink", ""),
                "snippet": (
                    f"Authors: {', '.join(info.get('authors', []))}\n"
                    f"Published: {info.get('publishedDate', 'Unknown')}\n"
                    f"{(info.get('description') or '')[:1000]}"
                )
            })

        if not book_items:

            results.append({
                "source_type": "Research warning",
                "title": "No books found",
                "url": "",
                "snippet": "Google Books returned no matching books for this topic."
            })

    except requests.RequestException as exc:

        results.append({
            "source_type": "Research warning",
            "title": "Book search unavailable",
            "url": "",
            "snippet": str(exc)
        })

    # --------------------------------------------------
    # 3. YOUTUBE VIDEO RESEARCH
    # --------------------------------------------------

    youtube_key = os.getenv("YOUTUBE_API_KEY")

    if not youtube_key:

        results.append({
            "source_type": "Research warning",
            "title": "YouTube API key not configured",
            "url": "",
            "snippet": "Add YOUTUBE_API_KEY to your .env file."
        })

    else:

        try:

            response = make_request(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "key": youtube_key,
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": 5,
                    "safeSearch": "strict",
                    "order": "relevance",
                    "videoEmbeddable": "true"
                },
                timeout=20
            )

            video_items = response.json().get("items", [])

            for item in video_items:

                video_id = item.get("id", {}).get("videoId")

                if not video_id:
                    continue

                snippet = item.get("snippet", {})

                results.append({
                    "source_type": "YouTube",
                    "title": snippet.get("title", "Educational video"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "snippet": (
                        f"Channel: {snippet.get('channelTitle', 'Unknown')}\n"
                        f"Published: {snippet.get('publishedAt', 'Unknown')}\n"
                        f"{snippet.get('description', '')[:1000]}"
                    )
                })

            if not video_items:

                results.append({
                    "source_type": "Research warning",
                    "title": "No YouTube videos found",
                    "url": "",
                    "snippet": "YouTube returned no matching videos."
                })

        except requests.RequestException as exc:

            results.append({
                "source_type": "Research warning",
                "title": "YouTube search unavailable",
                "url": "",
                "snippet": str(exc)
            })

    return results
