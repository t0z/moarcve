from sqlalchemy import Column, String, Integer, UniqueConstraint, DateTime
from moarcve.database.base import Base


class Cve(Base):

    __tablename__ = 'cve'

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    cve_id = Column(Integer)
    summary = Column(String(1024))
    vulnerable_configuration = Column(String(1024))
    vulnerable_sofware_list = Column(String(1024))
    cvss = Column(String(1024))
    published_datetime = Column(String())
    last_modified_datetime = Column(String())
    references = Column(String(1024))
    UniqueConstraint('cveid')
