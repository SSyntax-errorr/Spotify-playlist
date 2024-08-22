from dotenv import load_dotenv
import os
from flask import Flask, request, redirect, session
import requests
#import base64
#import json
#import spotipy
#from spotipy.oauth2 import SpotifyOAuth


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = 'http://localhost:8888/callback'


print(client_secret)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY");

@app.route('/')
def index():
    scopes = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}&show_dialog=true"
    
    return redirect(auth_url)


@app.route('/callback')
def callback():
    auth_code = request.args.get('code')

    if auth_code is None:
        return "Error: Authorization code is missing", 400
    
    
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()
    

    access_token = response_data.get('access_token')

    session['access_token'] = access_token

    return redirect('/playlists')
    


@app.route('/playlists')
def playlists():
    access_token = session.get('access_token')
    if not access_token:
        return "Error: Access token not found. Please authorize first."

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    playlists_url = 'https://api.spotify.com/v1/me/playlists'

    # Get my playlists
    response = requests.get(playlists_url, headers=headers)
    playlists_data = response.json()

    # Process playlists_data as needed
    playlists = playlists_data.get('items', [])

    tracks_to_add = None

    for playlist in playlists:

        
        playlist_to_remove = None
        if playlist.get('name', '') == '⟳':
            playlist_to_remove = playlist.get("id")
            tracks_url = f'https://api.spotify.com/v1/playlists/{playlist.get("id")}/tracks'
            response_tracks = requests.get(tracks_url, headers=headers)
            tracks_data = response_tracks.json()

            track_ids = [track['track']['id'] for track in tracks_data['items']]

            tracks_to_add = track_ids
        
    playlist_to_append = None    
    for playlist_b in playlists:
        if playlist_b.get('name', '') == '⟳⟳':
          playlist_to_append =  playlist_b.get("id")
        

    

    add_track_url = f"https://api.spotify.com/v1/playlists/{playlist_to_append}/tracks"

    for track_id in tracks_to_add:
        track_uri = f'spotify:track:{track_id}'
        data_add = {
            'uris': [track_uri]
        }   
            
        response_add = requests.post(add_track_url, headers=headers, json=data_add)
        if response_add.status_code == 201:
            print( "Track successfully added to playlist!")
            
            remove_track_url = f"https://api.spotify.com/v1/playlists/{playlist_to_remove}/tracks"
            data_remove = {
            'tracks': [{'uri': track_uri}]}

            
            response_remove = requests.delete(remove_track_url, headers=headers, json=data_remove)
            
            print (f"Failed to delete track from playlist.") 


        else:
            print (f"Failed to add track to playlist.") 


        
        

    


    
    #print(playlists)
    return f"User's Playlists: {playlists}"


if __name__ == '__main__':
    app.run(port=8888)



