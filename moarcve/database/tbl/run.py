from sqlalchemy import Column, String, Integer, DateTime
from moarcve.database.base import Base


class Run(Base):

    __tablename__ = 'run'

    id = Column(Integer, primary_key=True)
    started_on = Column(DateTime)
    stopped_on = Column(DateTime)
    status = Column(String)
    error = Column(String)
