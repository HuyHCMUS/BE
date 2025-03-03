from app.models.base import Base
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP, func,MetaData, DateTime
from sqlalchemy.orm import relationship
# Tạo metadata với schema content
metadata = MetaData(schema="content")
Base = declarative_base(metadata=metadata)

# SQLAlchemy Models
class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    practice_type = Column(String(20), nullable=False)
    question_type = Column(String(20), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    parent_id = Column(Integer, ForeignKey("content.questions.question_id"), nullable=True)


    # Relationships
    metadata_items = relationship("QuestionMetadata", back_populates="question", cascade="all, delete-orphan")
    content_items = relationship("QuestionContent", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    parent = relationship("Question", remote_side=[question_id], backref="children")


class QuestionMetadata(Base):
    __tablename__ = "question_metadata"

    metadata_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("content.questions.question_id", ondelete="CASCADE"), nullable=False)
    key = Column(String(50), nullable=False)
    value = Column(Text, nullable=False)

    # Relationship
    question = relationship("Question", back_populates="metadata_items")


class QuestionContent(Base):
    __tablename__ = "question_content"

    content_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("content.questions.question_id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    passage_text = Column(Text, nullable=True)

    # Relationships
    question = relationship("Question", back_populates="content_items")
    


class Answer(Base):
    __tablename__ = "answer"

    answer_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("content.questions.question_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    option_order = Column(Integer, nullable=False)
    hint = Column(Text, nullable=True)
    answer_type = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    # Relationship
    question = relationship("Question", back_populates="answers")

