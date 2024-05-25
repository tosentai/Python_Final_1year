from typing import Optional, List, Type
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from starlette.responses import FileResponse
import os
import random
from models import SoundsBase

url = URL.create(
    drivername="postgresql",
    host="localhost",
    port=5432,
    database="postgres",
    username="postgres",
    password="postgres"
)

engine = create_engine(url)

Session = sessionmaker(bind=engine)
session = Session()


class Music(BaseModel):
    id: Optional[PositiveInt] = None
    name: str = Field(min_length=1, max_length=30)
    author: str = Field(min_length=1, max_length=30)
    size: PositiveFloat


class MusicInfo(BaseModel):
    id: PositiveInt
    name: str
    author: str
    size: str


class MusicManager:
    def __init__(self):
        self.session = Session()

    def add_music(self, music: Music, file_data: bytes):
        project_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_folder, "music_files", f"{music.name}.mp3")

        with open(file_path, "wb") as f:
            f.write(file_data)

        db_music = SoundsBase(name=music.name, author=music.author, size=music.size, file_path=file_path)
        self.session.add(db_music)
        self.session.commit()
        self.session.refresh(db_music)
        return db_music

    def get_music(self, music_id: int) -> Type[SoundsBase]:
        try:
            return self.session.query(SoundsBase).filter_by(id=music_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="А нема такої музики з таким id")

    def get_all_music_info(self) -> List[MusicInfo]:
        music_info_list = []
        music_records = self.session.query(SoundsBase).all()
        for music in music_records:
            size_formatted = f"{music.size} MB"
            music_info_list.append(MusicInfo(id=music.id, name=music.name, author=music.author, size=size_formatted))
        return music_info_list

    def update_music(self, music_id: int, new_name: str, new_author: str, new_size: float, new_file_data: bytes = None):
        db_music = self.get_music(music_id)
        db_music.name = new_name
        db_music.author = new_author
        db_music.size = new_size

        if new_file_data:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_files", f"{new_name}.mp3")
            if os.path.exists(db_music.file_path):
                os.remove(db_music.file_path)
            with open(file_path, "wb") as f:
                f.write(new_file_data)
            db_music.file_path = file_path

        self.session.commit()

    def delete_music(self, music_id: int):
        db_music = self.get_music(music_id)
        if os.path.exists(db_music.file_path):
            os.remove(db_music.file_path)
        self.session.delete(db_music)
        self.session.commit()

    def delete_all_music(self):
        music_records = self.session.query(SoundsBase).all()
        num_deleted = 0
        for music in music_records:
            if os.path.exists(music.file_path):
                os.remove(music.file_path)
            self.session.delete(music)
            num_deleted += 1
        self.session.commit()

    def create_playlist(self, track_count: int) -> List[MusicInfo]:
        all_music = self.session.query(SoundsBase).all()
        if track_count > len(all_music):
            raise HTTPException(status_code=400,
                                detail="Недостатньо треків в базі даних для створення плейлиста з вказаною кількістю треків")

        selected_tracks = random.sample(all_music, track_count)
        return [MusicInfo(id=track.id, name=track.name, author=track.author, size=f"{track.size} MB") for track in
                selected_tracks]


app = FastAPI(title="Final project", version="1.1.0", description="<h2>by Anton Anpilohov</h2>")
music_manager = MusicManager()


@app.post("/upload/", response_model=Music)
async def upload_music(file: UploadFile = File(...), name: str = "", author: str = "", size: float = 0.0):
    if not file.filename.endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Тільки мп3шки дозволені")

    file_data = await file.read()
    music = Music(name=name, author=author, size=size)
    db_music = music_manager.add_music(music, file_data)
    return Music(id=db_music.id, name=db_music.name, author=db_music.author, size=db_music.size)


@app.get("/download/{music_id}")
async def download_music(music_id: int):
    db_music = music_manager.get_music(music_id)
    return FileResponse(db_music.file_path, media_type="audio/mpeg")


@app.get("/music_names/", response_model=List[MusicInfo])
async def get_music_names():
    music_info_list = music_manager.get_all_music_info()
    return music_info_list


@app.get("/music/{music_id}", response_model=MusicInfo)
async def get_music_info(music_id: int):
    db_music = music_manager.get_music(music_id)
    size_formatted = f"{db_music.size} MB"
    return MusicInfo(id=db_music.id, name=db_music.name, author=db_music.author, size=size_formatted)


@app.get("/playlist/{track_count}", response_model=List[MusicInfo])
async def create_playlist(track_count: int):
    playlist = music_manager.create_playlist(track_count)
    return playlist


@app.put("/music/{music_id}")
async def update_music(music_id: int, name: str = "", author: str = "", size: float = 0.0, file: UploadFile = File(None)):
    music_manager.update_music(music_id, name, author, size, file.file.read() if file else None)
    return {"message": "Інформацію про трек змінено"}


@app.delete("/music/{music_id}")
async def delete_music(music_id: int):
    music_manager.delete_music(music_id)
    return {"message": "Трек успішно видалено"}


@app.delete("/music/")
async def delete_all_music():
    music_manager.delete_all_music()
    return {"message": "Всі треки видалено"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3333, log_level="info")
