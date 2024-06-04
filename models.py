from sqlalchemy import Column, Integer, String, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)

    tracks = relationship("SoundsBase", back_populates="album", cascade="all, delete-orphan")


class SoundsBase(Base):
    __tablename__ = "musics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    size = Column(Float, nullable=False)
    file_path = Column(String, nullable=False)
    album_id = Column(Integer, ForeignKey('albums.id'))

    album = relationship("Album", back_populates="tracks")
