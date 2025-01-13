# app/models/db_models.py
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    overall_score = Column(Float)
    interpretation = Column(String)
    category_averages = Column(JSON)
    response_distribution = Column(JSON)
    responses = relationship("Response", back_populates="survey")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    question_idx = Column(Integer)
    score = Column(Integer)
    category = Column(String)
    survey = relationship("Survey", back_populates="responses")
