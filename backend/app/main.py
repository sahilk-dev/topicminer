from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, Comment
from app.services.youtube import extract_video_id, fetch_comments
from app.services.classify import classify_comments_in_batches
from app.models import CommentClassification

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


@app.post("/videos/{video_id}/classify")
def classify_video_comments(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.youtube_video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found — analyze it first")

    comments = db.query(Comment).filter(Comment.video_id == video.id).all()
    comment_dicts = [{"id": str(c.id), "body": c.body} for c in comments]

    classifications = classify_comments_in_batches(comment_dicts)

    for result in classifications:
        db.add(CommentClassification(
            comment_id=result["id"],
            category=result["category"],
            confidence=result.get("confidence"),
        ))
    db.commit()

    return {"classified_count": len(classifications)}