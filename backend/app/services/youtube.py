import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def get_youtube_client():
    """
    Create and return a YouTube API client using the API key
    stored in the .env file.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set")
    return build("youtube", "v3", developerKey=api_key)

def extract_video_id(url: str) -> str:
    """
    Extract and return the video ID from a YouTube URL.
    Supports both normal and shortened YouTube links.
    """
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    raise ValueError("Could not extract video ID from URL")

def fetch_comments(video_id: str, max_results: int = 100) -> list[dict]:
    """
    Fetch top-level comments from a YouTube video and
    return them as a list of dictionaries.
    """
    youtube = get_youtube_client()
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText",
    )
    response = request.execute()

    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet["authorDisplayName"],
            "text": snippet["textDisplay"],
            "like_count": snippet["likeCount"],
            "published_at": snippet["publishedAt"],
        })

    return comments