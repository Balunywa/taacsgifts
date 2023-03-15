from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField

class SearchForm(FlaskForm):
    search_term = StringField('Search Term')
    submit = SubmitField('Search')

class PlaylistForm(FlaskForm):
    name = StringField('Name')
    description = StringField('Description')
    cover_art = StringField('Cover Art')
    submit = SubmitField('Create Playlist')

class AddSongForm(FlaskForm):
    playlist_id = IntegerField('Playlist ID')
    submit = SubmitField('Add Song')