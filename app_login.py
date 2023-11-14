import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Function to initialize the Spotify client
@st.cache_resource
def initialize_spotify_client():
    CLIENT_ID = "5e56780c9b2f41bf9ae19268ebf30cea"
    CLIENT_SECRET = "e283afdd4ee84b2a8dc666a97236588e"
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

# Function to get song album cover URL
def get_song_album_cover_url(sp, song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

# Function to recommend music
def recommend_music(sp, music, similarity, selected_music):
    index = music[music['song'] == selected_music].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_music_posters.append(get_song_album_cover_url(sp, music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)

    return recommended_music_names, recommended_music_posters

# Main function
def main():
    st.header('-[ Musica Reksis ]-\nThe Music Recommendation System')

    # User Login
    st.sidebar.header("User Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        # Placeholder for login logic
        st.sidebar.success("Login successful! 🎉")

    # User Signup
    st.sidebar.header("User Signup")
    new_email = st.sidebar.text_input("New Email")
    new_password = st.sidebar.text_input("New Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")

    if new_password != confirm_password:
        st.sidebar.warning("Passwords do not match.")
    elif st.sidebar.button("Sign Up"):
        # Placeholder for signup logic
        st.sidebar.success("Account created successfully! You can now log in.")

    # Initialize Spotify client (this is done only once)
    sp = initialize_spotify_client()

    # Load music data and similarity matrix
    music = pickle.load(open('df.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    music_list = music['song'].values
    selected_music = st.selectbox(
        "Type or select a song from the dropdown",
        music_list
    )

    if st.button('Show Recommendation'):
        recommended_music_names, recommended_music_posters = recommend_music(sp, music, similarity, selected_music)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(recommended_music_names[0])
            st.image(recommended_music_posters[0])
        with col2:
            st.text(recommended_music_names[1])
            st.image(recommended_music_posters[1])
        with col3:
            st.text(recommended_music_names[2])
            st.image(recommended_music_posters[2])
        with col4:
            st.text(recommended_music_names[3])
            st.image(recommended_music_posters[3])
        with col5:
            st.text(recommended_music_names[4])
            st.image(recommended_music_posters[4])

if __name__ == "__main__":
    main()
