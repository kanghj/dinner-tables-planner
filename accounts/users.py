import datetime

from sqlalchemy import Column, Integer, String, select, DateTime
from .db import Base, db_session


from datetime import timedelta



def jobs_of_user(user_id):
    s = db_session.query(UserJobs)
    user_jobs = s.filter(UserJobs.id == user_id)
    return user_jobs

def clear_old():
    dates = db_session.query(JobDates)
    user_jobs = db_session.query(UserJobs)

    date_3_weeks_ago = datetime.datetime.now() - timedelta(weeks=3)

    old = dates.filter(JobDates.date_created <= date_3_weeks_ago)

    job_ids = [old_job.id for old_job in old]

    user_jobs.filter(UserJobs.job_id.in_(job_ids)).delete(synchronize_session='fetch')
    old.delete()

    db_session.commit()

class UserJobs(Base):
    __tablename__ = 'user_jobs'
    id = Column(String, primary_key=True)
    job_id = Column(String, primary_key=True)

    def __init__(self, id=None, job_id=None):
        self.id = id
        self.job_id = job_id

    def __repr__(self):
        return '<User %r %s>' % (self.name, self.job_id)

class JobDates(Base):
    __tablename__ = 'job_dates'
    id = Column(String, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)