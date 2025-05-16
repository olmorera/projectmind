# db/models/project.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from db.models.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
