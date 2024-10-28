# 🎥 Video to Blog Generator

This project transforms video content into a comprehensive blog post by identifying "stable frames" — parts of the video where frames change very little over a specified period. Using both visual and audio analysis, the tool captures important moments, extracts still frames, and transcribes any voice-over present during these segments. The final result is a blog-ready summary of the video content.

## Project Workflow

### **1. Frame Extraction**
The process starts with loading the video and capturing frames at a set frame rate. This step is managed by the `extract_video_frames` function, which:

- Loads the video using OpenCV.
- Processes each frame and stores it in a format ready for comparison.
- Adds each frame to a list for the next stages.

### **2. Frame Similarity Measurement**
To detect similar frames, we calculate the similarity between consecutive frames. Several methods can be used here:

- **Pixel-by-Pixel Comparison**: Compares two frames using L2 norm.
- **Structural Similarity Index (SSIM)**: Measures pixel-wise similarity to provide a similarity score.
- **Histogram Comparison**: Compares color histograms as an alternative to SSIM.
- **Image Encoding**: Uses pre-trained models to encode frames and calculate cosine similarity.

In this project, I used the SSIM method, but you can experiment with other similarity techniques as well.

### **3. Detecting Stable Frames**
The core logic for stability detection is in the `find_stable_frames` function. This function:

- Compares each frame to the next, checking if the similarity score meets the given threshold.
- Counts consecutive frames as "stable" if their similarity remains above the threshold.
- Records the start and end timestamps of stable frame sequences that last over the specified duration.

### **4. Audio Processing**
This step focuses on capturing and transcribing the audio from the video:

- Extracts the audio track.
- Transcribes the audio using the Faster-Whisper tool, which provides start and end timestamps for each spoken segment.

### **5. Matching Audio to Stable Frames**
With both stable frames and transcribed audio segments available, the next step is to align the two:

- Matches each stable frame's start and end time with the corresponding transcription segment, ensuring the right text is paired with each stable frame section.

### **6. Generating the Blog Post in HTML**
The final step is to create a blog post using the stable frames and transcribed text:

- The tool generates a structured HTML page, combining images from the stable frames with their matched transcriptions for a visually organized and readable blog post.

This process results in a polished, blog-ready summary of the video content, with key moments captured in both visual and text format.


## Usage

1. **Clone the Git Repository**  
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
2. **Create a Virtual Environment and Activate It**

- For Windows:
    ```bash
    python -m venv env
    .\env\Scripts\activate
    ```
- For MacOS/Linux:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. **Install Requirements**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Streamlit Application**
    ```bash
    streamlit run app.py
    ```

### Using Docker

```bash
docker-compose up --build
```

This will start the application on localhost:8501. Open the link in your browser to access the Video to Blog Post Generator.
