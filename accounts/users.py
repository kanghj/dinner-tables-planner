from sqlalchemy import Column, Integer, String
from .db import Base


class UserJobs(Base):
    __tablename__ = 'user_jobs'
    id = Column(Integer, primary_key=True)
    job_id = Column(String, primary_key=True)

    def __init__(self, id=None, job_id=None):
        self.id = id
        self.job_id = job_id

    def __repr__(self):
        return '<User %r %s>' % (self.name, self.job_id)