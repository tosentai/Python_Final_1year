from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from starlette.responses import FileResponse
import os
import random
from models import SoundsBase, Album as AlbumModel

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


class AlbumSchema(BaseModel):
    id: Optional[PositiveInt] = None
    name: str = Field(min_length=1, max_length=30)
    artist: str = Field(min_length=1, max_length=30)


class AlbumInfo(BaseModel):
    id: PositiveInt
    name: str
    artist: str
    tracks: List[MusicInfo]


class MusicManager:
    def __init__(self):
        self.session = Session()

    def add_music(self, music: Music, file_data: bytes, album_id: Optional[int] = None):
        project_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_folder, "music_files", f"{music.name}.mp3")

        with open(file_path, "wb") as f:
            f.write(file_data)

        db_music = SoundsBase(name=music.name, author=music.author, size=music.size, file_path=file_path, album_id=album_id)
        self.session.add(db_music)
        self.session.commit()
        self.session.refresh(db_music)
        return db_music

    def get_music(self, music_id: int) -> SoundsBase:
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

    def update_music(self, music_id: int, new_name: str, new_author: str, new_size: float, new_file_data: bytes = None, album_id: Optional[int] = None):
        db_music = self.get_music(music_id)
        db_music.name = new_name
        db_music.author = new_author
        db_music.size = new_size
        db_music.album_id = album_id

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
        sql_statement = text(f"ALTER SEQUENCE {SoundsBase.__table__.name}_id_seq RESTART WITH 1")
        self.session.execute(sql_statement)
        self.session.commit()

    def create_playlist(self, track_count: int) -> List[MusicInfo]:
        all_music = self.session.query(SoundsBase).all()
        if track_count > len(all_music):
            raise HTTPException(status_code=400,
                                detail="Недостатньо треків в базі даних для створення плейлиста з вказаною кількістю треків")

        selected_tracks = random.sample(all_music, track_count)
        return [MusicInfo(id=track.id, name=track.name, author=track.author, size=f"{track.size} MB") for track in
                selected_tracks]

    def add_album(self, album: AlbumSchema):
        db_album = AlbumModel(name=album.name, artist=album.artist)
        self.session.add(db_album)
        self.session.commit()
        self.session.refresh(db_album)
        return db_album

    def get_album(self, album_id: int) -> AlbumModel:
        try:
            return self.session.query(AlbumModel).filter_by(id=album_id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Альбом не знайдений")

    def get_all_albums_info(self) -> List[AlbumInfo]:
        albums_info_list = []
        albums = self.session.query(AlbumModel).all()
        for album in albums:
            tracks = [MusicInfo(id=track.id, name=track.name, author=track.author, size=f"{track.size} MB") for track in album.tracks]
            albums_info_list.append(AlbumInfo(id=album.id, name=album.name, artist=album.artist, tracks=tracks))
        return albums_info_list

    def update_album(self, album_id: int, new_name: str, new_artist: str):
        db_album = self.get_album(album_id)
        db_album.name = new_name
        db_album.artist = new_artist
        self.session.commit()

    def delete_album(self, album_id: int):
        db_album = self.get_album(album_id)
        tracks = db_album.tracks
        for track in tracks:
            self.delete_music(track.id)
        self.session.delete(db_album)
        self.session.commit()

    def delete_all_albums(self):
        albums = self.session.query(AlbumModel).all()
        for album in albums:
            tracks = album.tracks
            for track in tracks:
                self.delete_music(track.id)
            self.session.delete(album)
        self.session.commit()
        sql_statement = text(f"ALTER SEQUENCE {AlbumModel.__table__.name}_id_seq RESTART WITH 1")
        self.session.execute(sql_statement)
        self.session.commit()


app = FastAPI(title="Final project", version="1.2.0", description="<h2>by Anton Anpilohov</h2>")
music_manager = MusicManager()


@app.post("/upload/", response_model=Music)
async def upload_music(file: UploadFile = File(...), name: str = "", author: str = "", size: float = 0.0, album_id: Optional[int] = None):
    if not file.filename.endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Тільки мп3шки дозволені")

    file_data = await file.read()
    music = Music(name=name, author=author, size=size)
    db_music = music_manager.add_music(music, file_data, album_id)
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
async def update_music(music_id: int, name: str = "", author: str = "", size: float = 0.0, file: UploadFile = File(None), album_id: Optional[int] = None):
    music_manager.update_music(music_id, name, author, size, await file.read() if file else None, album_id)
    return {"message": "Інформацію про трек змінено"}


@app.delete("/music/{music_id}")
async def delete_music(music_id: int):
    music_manager.delete_music(music_id)
    return {"message": "Трек успішно видалено"}


@app.delete("/music/")
async def delete_all_music():
    music_manager.delete_all_music()
    return {"message": "Всі треки видалено"}


@app.post("/albums/", response_model=AlbumSchema)
async def create_album(album: AlbumSchema):
    db_album = music_manager.add_album(album)
    return AlbumSchema(id=db_album.id, name=db_album.name, artist=db_album.artist)


@app.get("/albums/", response_model=List[AlbumInfo])
async def get_albums():
    albums_info_list = music_manager.get_all_albums_info()
    return albums_info_list


@app.get("/albums/{album_id}", response_model=AlbumInfo)
async def get_album(album_id: int):
    db_album = music_manager.get_album(album_id)
    tracks = [MusicInfo(id=track.id, name=track.name, author=track.author, size=f"{track.size} MB") for track in db_album.tracks]
    return AlbumInfo(id=db_album.id, name=db_album.name, artist=db_album.artist, tracks=tracks)


@app.put("/albums/{album_id}")
async def update_album(album_id: int, name: str = "", artist: str = ""):
    music_manager.update_album(album_id, name, artist)
    return {"message": "Інформація про альбом змінена"}


@app.delete("/albums/{album_id}")
async def delete_album(album_id: int):
    music_manager.delete_album(album_id)
    return {"message": "Альбом успішно видалений"}


@app.delete("/albums/")
async def delete_all_albums():
    music_manager.delete_all_albums()
    return {"message": "Всі альбоми видалено"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3333, log_level="info")
