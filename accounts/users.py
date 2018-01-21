from sqlalchemy import Column, Integer, String, select
from .db import Base, db_session


def jobs_of_user(user_id):
    s = db_session.query(UserJobs)
    user_jobs = s.filter(UserJobs.id == user_id)
    return user_jobs

class UserJobs(Base):
    __tablename__ = 'user_jobs'
    id = Column(String, primary_key=True)
    job_id = Column(String, primary_key=True)

    def __init__(self, id=None, job_id=None):
        self.id = id
        self.job_id = job_id

    def __repr__(self):
        return '<User %r %s>' % (self.name, self.job_id)