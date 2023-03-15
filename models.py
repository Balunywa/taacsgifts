import pyodbc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    shares = db.relationship('Share', backref='user', lazy=True)
    selected_songs = db.relationship('SelectedSong', backref='user', lazy=True)

class SelectedSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    track_id = db.Column(db.Integer)
    track_name = db.Column(db.String(255))
    artist_name = db.Column(db.String(255))
    album_name = db.Column(db.String(255))
    preview_url = db.Column(db.String(255))
    artwork_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
class DJ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    cover_art = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dj_id = db.Column(db.Integer, db.ForeignKey('dj.id'), nullable=True)
    share_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('Song', backref='playlist', primaryjoin='and_(Playlist.id==Song.playlist_id)')
    shares = db.relationship('Share', backref='playlist', lazy=True)


    
class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    
    performers = db.relationship(
        'Musician', secondary='song_performers',
        primaryjoin='Song.id==song_performers.c.song_id',
        secondaryjoin='Musician.id==song_performers.c.musician_id',
        backref='songs', lazy=True
    )

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    albums = db.relationship('Album', backref='artist', lazy=True)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    songs = db.relationship('Song', backref='album', lazy=True)

class Musician(db.Model):
    __tablename__ = 'musicians'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class MusicianAlbum(db.Model):
    __tablename__ = 'musician_album'
    musician_id = db.Column(db.Integer, db.ForeignKey('musicians.id'), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), primary_key=True)


song_performers = db.Table('song_performers',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('musician_id', db.Integer, db.ForeignKey('musicians.id'), primary_key=True)
)


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer)
    track_name = db.Column(db.String(255))
    artist_name = db.Column(db.String(255))
    album_name = db.Column(db.String(255))
    preview_url = db.Column(db.String(255))
    artwork_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)