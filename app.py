import os
import streamlit as st
from utils.video2blog import VideoToBlog
import streamlit.components.v1 as components
from utils.helper import create_blog_post

# Streamlit page configuration
st.set_page_config(page_title="🎥 Video to Blog Generator", layout="wide")

# Title and Description
# st.title("🎥 Video to Blog Post Generator")

# Sidebar for inputs
st.sidebar.header("🎥 Video to Blog")
video_file = st.sidebar.file_uploader("Upload a video file", type=["mp4"])
title = st.sidebar.text_input("Blog Title", placeholder="Enter your blog title")
stable_duration_sec = st.sidebar.slider("Stable Frame Duration (seconds)", min_value=1, max_value=10, value=5, step=1, help="Specify the duration a frame must appear to be considered stable.")

# Process video if inputs are provided
if st.sidebar.button("Generate Blog Post"):
    if video_file and title and stable_duration_sec:
        # Save video file temporarily
        with open("temp_video.mp4", "wb") as f:
            f.write(video_file.read())
        
        with st.spinner("Extracting Frames From the Video...."):
            print("***************** Extracting Frames From the Video *****************************")
            # Initialize and process with the VideoToBlog model
            model = VideoToBlog(video_path="temp_video.mp4", title=title, stable_duration_sec=stable_duration_sec)
            frames,frame_rate = model.extract_video_frames()
            print(f"Extracted {len(frames)} frames.")

        with st.spinner("Finding The Stable Frames From The Video...."):
            print("***************** Finding The Stable Frames From The Video **********************")
            stable_frames, start_and_end_frame = model.find_stable_frames(frames, frame_rate)
            # print("***************** Transcribing The Audio ****************************")
        
        with st.spinner("Transcribing Audio...."):
            model.extract_audio()
            transcripton = model.transcribe_audio()
            final_text = model.map_frames_and_transcription(start_and_end_frame,transcripton)
            # transcripton = model.split_audio_with_ffmpeg("audio.mp3",start_and_end_frame)
            blog_post_path = create_blog_post(model.title,stable_frames,final_text)

            if blog_post_path:

                st.toast("Your Blog Post is Ready...")
        
        # Display the blog post
        st.subheader("Generated Blog Post")
        with open(blog_post_path, "r") as blog_file:
            blog_content = blog_file.read()
            components.html(blog_content, height=4000, scrolling=True)


            st.download_button(label="Download and View Blog Post", 
                    data=blog_content, 
                    file_name="generated_blog_post.html", 
                    mime="text/html")
        
        st.success("Blog post generated successfully!")
    else:
        st.error("Please upload a video, set a title, and specify the stable frame duration.")




