import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    youtube_video_id = Column(String, unique=True, nullable=False)
    comment_count = Column(Integer, default=0)

    comments = relationship("Comment", back_populates="video")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    author = Column(String)
    body = Column(String)
    like_count = Column(Integer, default=0)
    published_at = Column(DateTime)

    video = relationship("Video", back_populates="comments")

class CommentClassification(Base):
    __tablename__ = "comment_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=False)
    category = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)

    comment = relationship("Comment")