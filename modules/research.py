import os
import requests

def collect_research(title: str, objective: str):
    """Collect web, book and YouTube metadata. Missing optional keys do not stop the workflow."""
    results = []
    query = f"{title} {objective}"

    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "search_depth": "advanced",
                      "max_results": 5, "include_answer": False},
                timeout=25
            )
            response.raise_for_status()
            for item in response.json().get("results", []):
                results.append({
                    "source_type": "Website",
                    "title": item.get("title", "Web result"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")
                })
        except requests.RequestException as exc:
            results.append({"source_type": "Research warning", "title": "Web search unavailable",
                            "url": "", "snippet": str(exc)})

    try:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": title, "maxResults": 5}, timeout=20
        )
        response.raise_for_status()
        for item in response.json().get("items", []):
            info = item.get("volumeInfo", {})
            results.append({
                "source_type": "Book",
                "title": info.get("title", "Book"),
                "url": info.get("infoLink", ""),
                "snippet": (info.get("description") or "")[:1200]
            })
    except requests.RequestException:
        pass

    youtube_key = os.getenv("YOUTUBE_API_KEY")
    if youtube_key:
        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={"key": youtube_key, "part": "snippet", "q": query,
                        "type": "video", "maxResults": 5, "safeSearch": "strict"},
                timeout=20
            )
            response.raise_for_status()
            for item in response.json().get("items", []):
                video_id = item["id"].get("videoId")
                if video_id:
                    snippet = item.get("snippet", {})
                    results.append({
                        "source_type": "YouTube",
                        "title": snippet.get("title", "Video"),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "snippet": snippet.get("description", "")
                    })
        except requests.RequestException:
            pass

    return results
