import os
import streamlit as st
from langchain.llms import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

st.set_page_config(page_title="Mood Music Matcher", page_icon="🎵", layout="wide")

st.title('Mood Music Matcher 🎵')

openai_api_key = os.getenv("OPEN_AI_KEY")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

st.sidebar.markdown(
    """
    ## App Description
    **Mood Music Matcher** enhances your day by providing music that matches your mood. Integrated with Spotify, it offers seamless access to songs.

    ### Benefits
    - **Personalized Recommendations**: Get songs based on your feelings.
    - **Mood Analysis**: Gain insights into your emotional state.
    - **Spotify Integration**: Directly listen to curated tracks via Spotify.

    ### How to Use
    1. **Enter Your Journal Entry**: Share your day or thoughts.
    2. **Analyze Mood**: The app uses AI to determine your mood.
    3. **Get Music Suggestions**: Discover songs that resonate with you.
    4. **Listen and Enjoy**: Click the link to be automatically directed to Spotify and play the song.
    """
)

def analyze_mood(input_text):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    mood_analysis = llm(f"Identify the mood of this text for music recommendation: {input_text}")
    return mood_analysis.strip().lower()

def get_songs_for_mood(mood):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret))
    results = sp.search(q=mood, type='track', limit=5, market='US')
    return [(track['name'], track['artists'][0]['name'], track['external_urls']['spotify']) for track in results['tracks']['items']]

def explain_song_choice(mood, track_name, artist):
    llm = OpenAI(temperature=0.2, openai_api_key=openai_api_key)
    explanation = llm(f"Explain why the song '{track_name}' by {artist} matches the mood '{mood}' based on its musical style and mood, without referring to the lyrics.")
    return explanation

with st.form('journal_form'):
    journal_text = st.text_area(
        '✨ Describe Your Day, Today:',
        placeholder='E.g., Today was quite challenging, but I managed to push through and complete my tasks...',
        height=200
    )
    submitted = st.form_submit_button('Get Songs 🎶')
    
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        else:
            mood = analyze_mood(journal_text)
            st.subheader("Your Mood 🎭")
            st.write(f"It seems like you're feeling: **{mood}**")
            st.write("Let's find some popular songs that match your vibe. 🎧")
            song_list = get_songs_for_mood(mood)
            st.subheader("Suggested Songs 🎵")
            if song_list:
                for idx, (name, artist, url) in enumerate(song_list, start=1):
                    explanation = explain_song_choice(mood, name, artist)
                    st.write(f"{idx}. **{name}** by {artist} - [Listen on Spotify]({url}) 🎧")
                    st.write(f"This song fits your mood because: {explanation}")
            else:
                st.write("No suitable songs found.")
