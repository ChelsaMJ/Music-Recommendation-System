import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import json

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

    # Initialize session state if not already initialized
    if 'saved_recommendations' not in st.session_state:
        st.session_state.saved_recommendations = []

    st.header('-[ Musica Reksis ]-\n\tThe Music Recommendation System')
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    # User Login
    st.sidebar.header("LOGIN")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    login_button = st.sidebar.button("Login")

    if login_button:
        # Placeholder for login logic
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (email, password))
        user_id = cursor.fetchone()

        if user_id:
            st.sidebar.success("Login successful! 🎉")
            st.session_state.is_logged_in = True
        else:
            st.sidebar.error("Authentication failed. Please sign up or check your credentials.")
    
    st.sidebar.header("--------------------------------------------")
    
    # User Signup
    st.sidebar.header("SIGN UP")
    new_email = st.sidebar.text_input("New Email")
    new_password = st.sidebar.text_input("New Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")

    if new_password != confirm_password:
        st.sidebar.warning("Passwords do not match.")
    elif st.sidebar.button("Sign Up"):
        # Placeholder for signup logic
        st.sidebar.success("Account created successfully! You can now log in.")

    # Check if the user is logged in
    if getattr(st.session_state, 'is_logged_in', False):
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

            # Use st.checkbox for persistent checkboxes
            save_flags = [st.checkbox(f"Save ({recommended_music_names[i]})", key=f"checkbox_{i}") for i in range(5)]

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

            # Add selected songs to saved recommendations
            for i, flag in enumerate(save_flags):
                if flag:
                    st.session_state.saved_recommendations.append(recommended_music_names[i])

        # Update saved recommendations in session state
        if st.session_state.saved_recommendations:
            json_data = json.dumps(st.session_state.saved_recommendations)
            st.session_state.saved_recommendations_json = json_data

        # Load saved recommendations from session state
        if 'saved_recommendations_json' in st.session_state:
            saved_recommendations_json = st.session_state.saved_recommendations_json
            st.session_state.saved_recommendations = json.loads(saved_recommendations_json)
        else:
            st.session_state.saved_recommendations = []

        # Display saved recommendations in the right sidebar if the user is logged in
        if getattr(st.session_state, 'is_logged_in', False):
            st.sidebar.header("Saved Recommendations")
            saved_recommendations = st.sidebar.empty()

            # Check if there are saved recommendations
            if st.session_state.saved_recommendations:
                saved_recommendations.text("Your saved recommendations:")
                for saved_recommendation in st.session_state.saved_recommendations:
                    saved_recommendations.text(saved_recommendation)
            else:
                saved_recommendations.text("No saved recommendations yet.")

    # Close the database connection when done
    conn.close()

if __name__ == "__main__":
    main()
