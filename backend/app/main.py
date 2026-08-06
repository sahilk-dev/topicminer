from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, Comment
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
def analyze_video(request: VideoRequest, db: Session = Depends(get_db)):
    try:
        video_id = extract_video_id(request.url)
        comments = fetch_comments(video_id)

        video = db.query(Video).filter(Video.youtube_video_id == video_id).first()
        if not video:
            video = Video(youtube_video_id=video_id, comment_count=len(comments))
            db.add(video)
            db.commit()
            db.refresh(video)

        for c in comments:
            db.add(Comment(
                video_id=video.id,
                author=c["author"],
                body=c["text"],
                like_count=c["like_count"],
                published_at=c["published_at"],
            ))
        db.commit()

        return {"video_id": video_id, "comment_count": len(comments)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))