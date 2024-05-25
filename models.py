from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SoundsBase(Base):
    __tablename__ = "musics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    size = Column(Float, nullable=False)
    file_path = Column(String, nullable=False)