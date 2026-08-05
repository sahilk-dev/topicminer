from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.youtube import extract_video_id, fetch_comments

app = FastAPI(title="TopicMiner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/videos")
def analyze_video(request: VideoRequest):
    try:
        video_id = extract_video_id(request.url)
        comments = fetch_comments(video_id)
        return {"video_id": video_id, "comment_count": len(comments), "comments": comments}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))