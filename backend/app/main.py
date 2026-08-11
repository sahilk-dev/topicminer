from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, Comment
from app.services.youtube import extract_video_id, fetch_comments
from app.services.classify import classify_comments_in_batches
from app.models import CommentClassification
from app.services.cluster import extract_topic_label, cluster_labels, name_cluster
from app.models import TopicCluster
from collections import defaultdict

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

@app.post("/videos/{video_id}/cluster-topics")
def cluster_topics(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.youtube_video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    suggestions = (
        db.query(CommentClassification)
        .join(Comment)
        .filter(Comment.video_id == video.id, CommentClassification.category == "SUGGESTION")
        .all()
    )
    if not suggestions:
        return {"clusters": []}

    for s in suggestions:
        s.topic_label_raw = extract_topic_label(s.comment.body)
    db.commit()

    labels = [s.topic_label_raw for s in suggestions]
    cluster_indices = cluster_labels(labels)

    grouped = defaultdict(list)
    for classification, cluster_idx in zip(suggestions, cluster_indices):
        grouped[cluster_idx].append(classification)

    results = []
    for cluster_idx, members in grouped.items():
        member_labels = [m.topic_label_raw for m in members]
        cluster_name = name_cluster(member_labels)

        cluster = TopicCluster(
            video_id=video.id,
            cluster_name=cluster_name,
            mention_count=len(members)
        )
        db.add(cluster)
        db.commit()
        db.refresh(cluster)

        for m in members:
            m.cluster_id = cluster.id
        db.commit()

        results.append({"cluster_name": cluster_name, "mention_count": len(members)})

    results.sort(key=lambda r: r["mention_count"], reverse=True)
    for rank, r in enumerate(results, start=1):
        r["rank"] = rank

    return {"clusters": results}