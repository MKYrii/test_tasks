from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base
import enum


class TaskStatus(str, enum.Enum):
    IN_QUEUE = "In Queue"
    RUN = "Run"
    COMPLETED = "Completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default=TaskStatus.IN_QUEUE.value, nullable=False)
    create_time = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=True)
    exec_time = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "exec_time": self.exec_time
        }

    def to_response(self):
        return {
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "time_to_execute": self.exec_time
        }