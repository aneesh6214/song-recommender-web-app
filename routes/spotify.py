import spotipy, secrets, os, time
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, url_for, session, request, redirect
#import pandas as panda

#setup environment variables
load_dotenv()
env_client_id = os.environ.get('CLIENT_ID')
env_client_secret = os.environ.get('CLIENT_SECRET')

#app config
spotify_routes = Blueprint('spotify', __name__)

# ==========================
# ===== ROUTE HANDLING =====
# ==========================
@spotify_routes.route('/login')
def login():
    """
    Initiates the Spotify login flow.

    Redirects the user to the Spotify authorization page.
    """
    #use oauth to log user in
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)

@spotify_routes.route('/redirect')
def redirect_page():
    """
    Handles the redirect from the Spotify authorization page.

    Retrieves the access code from the redirect URL, exchanges it for an access token,
    and stores the token information in the session.
    """
    #create new authorization & clear session tokens
    sp_oauth = create_spotify_oauth()
    session.clear()

    #get access code & access token & store it in the session
    access_code = request.args.get('code')
    token_info = sp_oauth.get_access_token(access_code)
    session["token_info"] = token_info
    session["logged_in"] = True

    return redirect(url_for("spotify.get_tracks_route", _external=True))


@spotify_routes.route('/getTracks')
def get_tracks_route():
    results = get_top_tracks()
    return redirect("/")

@spotify_routes.route('/logout')
def logout():
    """
    Logs out the user by clearing the session.

    Redirects to the home page.
    """
    #clear the session
    session["logged_in"] = False
    for key in list(session.keys()):
        session.pop(key)
    
    return redirect('/')

# ===================
# ===== HELPERS =====
# ===================
def get_top_tracks():
    """
    Retrieves all tracks saved by the authenticated user.

    Returns a list of track names and artists.
    """
    #authorize user
    token = get_token()
    session['token_info'] = token
    authorized = token
    session.modified = True
    if not authorized:
        return redirect('/')
    
    #paginate through user data to get songs
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = fetch_tracks(sp.current_user_top_tracks, limit=50, time_range='medium_term')

    return results

def fetch_tracks(api_function, limit, **kwargs):
    """
    Helper function to fetch tracks using the provided API function.

    Returns a list of track names and artists.
    """
    tracks = api_function(limit=limit, **kwargs)['items']
    results = []

    for track in tracks:
        #format top_tracks response
        track_name = track['name']
        artist_name = track['artists'][0]['name'] if track['artists'] else ''

        if track_name and artist_name:
            val = f"{track_name} - {artist_name}"
            results.append(val)

    return results

def get_token():
    """
    Helper to retrieve the access token from the session.
    If the token has expired, refreshes it using the refresh token.

    Returns the token information.
    """
    #get token info from session data
    token_info = session.get("token_info", None)
    if not token_info:
        raise "Exception: Not Logged In"
    
    #refresh token if expired
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    """
    Creates a SpotifyOAuth object for the Spotify API authorization.

    Returns the SpotifyOAuth object.
    """
    return SpotifyOAuth(
        client_id=env_client_id,
        client_secret=env_client_secret,
        redirect_uri=url_for('spotify.redirect_page', _external=True),
        scope="user-library-read user-top-read"
    )