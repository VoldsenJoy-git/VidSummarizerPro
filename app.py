import streamlit as st
from dotenv import load_dotenv # Helps load environment variables from a .env file into the application.
import os
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound # Extracts transcripts from YouTube videos.
from googletrans import Translator
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key for Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the translator
translator = Translator()

# Prompt for AI model summarization
prompt = """
You are a YouTube video summarizer. Please summarize the transcript text below into concise points in 15 lines, write it in English only.
"""

# Function to extract transcript from a YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en','bn', 'hi', 'auto'])
        
        transcript = ""
        language = 'auto'  # Default language if none specified
        
        # Check the language from the transcript data
        for item in transcript_data:
            transcript += " " + item["text"]
            if not language and "language" in item:
                language = item["language"]
        return transcript, language
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
        return None, None
    except Exception as e:
        st.error(f"Error while fetching transcript: {str(e)}")
        return None, None

# Function to translate the transcript to English
def translate_to_english(transcript_text):
    try:
        if not transcript_text:
            st.error("The transcript is empty, cannot proceed with translation.")
            return None
        translated_text = translator.translate(transcript_text, dest="en").text
        return translated_text
    except Exception as e:
        st.error(f"Error during translation: {str(e)}")
        return None

# Function to generate a summary using Google Gemini AI
def generate_summary(translated_text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + translated_text)
        return response.text
    except Exception as e:
        st.error(f"Error during content generation: {str(e)}")
        return None

# Streamlit UI
st.title("YouTube Video Summarizer (Multilingual)")
youtube_link = st.text_input("Enter YouTube Video Link:")

 # If a video link is provided, extracts the video ID and displays the video's thumbnail.
if youtube_link:
    video_id = youtube_link.split("v=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Summarize Video"):
    try:
        # Extract the transcript
        transcript_text, language = extract_transcript_details(youtube_link)
        
        if transcript_text:
            st.success("Transcript Found!")
            st.subheader(f"Transcript Preview (Language: {language}):")
            st.write(transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text)
        
            summary = generate_summary(transcript_text)
            if summary:
                st.subheader("Video Summary:")
                st.write(summary)
                
    except Exception as e:
        st.error(f"Failed to process the video: {str(e)}") 