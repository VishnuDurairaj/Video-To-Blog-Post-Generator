import gc
import os
import cv2
import shutil
import ffmpeg
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
from utils.helper import create_blog_post
from skimage.metrics import structural_similarity as ssim


class VideoToBlog:

    def __init__(self,video_path,title,frame_interval=1,similarity_threshold=0.99,stable_duration_sec=5,transcription_model="large-v3",device="cpu",compute_type="int8"):
        self.video_path = video_path
        self.title=title
        self.frame_interval = frame_interval
        self.similarity_threshold = similarity_threshold
        self.stable_duration_sec = stable_duration_sec
        if os.path.isdir("stable_frames"):
            shutil.rmtree('stable_frames')
        os.makedirs("stable_frames",exist_ok=True)
        self.__transcription_model = WhisperModel(transcription_model, device=device, compute_type=compute_type)

    def extract_video_frames(self):
        """
        Extracts frames from a video at the specified interval.

        Parameters:
        - video_path (str): Path to the video file.
        - frame_interval (int): Interval at which frames are saved (e.g., 1 = every frame, 2 = every other frame).
        
        Returns:
        - frames (list): List of frames extracted from the video.
        """
        # Load the video
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return []

        # Retrieve frame rate to process frames efficiently
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        print(f"Frame rate: {frame_rate} FPS")

        frames = []
        frame_index = 0

        while True:
            ret, frame = cap.read()

            # Break the loop if there are no frames left to read
            if not ret:
                break

            # Process only every `frame_interval` frame
            if frame_index % self.frame_interval == 0:
                frames.append(frame)

            frame_index += 1

        cap.release()
        print(f"Total frames extracted: {len(frames)}")
        return frames, frame_rate

    def find_stable_frames(self,frames, frame_rate):
        """
        Identify stable frames in a list of video frames.

        Parameters:
        - frames (list): List of frames extracted from a video.
        - frame_rate (float): Frame rate of the video.
        - similarity_threshold (float): SSIM similarity threshold for consecutive frames to be considered stable.
        - stable_duration (float): Minimum duration in seconds for frames to be considered stable.

        Returns:
        - stable_frames (list): List of tuples with start and end timestamps for stable frames.
        """
        # Calculate the required consecutive stable frame count
        required_stable_frames = int(self.stable_duration_sec * frame_rate)
        stable_frames = []
        stable_frames_count=0
        start_and_end = []
        start_ind = None
        end_ind = None
        start_time = None
        end_time = None

        current_stable_frames = []

        for i in range(1, len(frames)):

            if i%100==0:

                print(f"processing : {i}/{len(frames)}")

            # Convert frames to grayscale
            frame1_gray = cv2.cvtColor(frames[i - 1], cv2.COLOR_BGR2GRAY)

            frame2_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

            similarity_score, _ = ssim(frame1_gray, frame2_gray, full=True)

            if similarity_score>=self.similarity_threshold:

                if not start_time:

                    start_ind = i-1

                    stable_frames_count +=1

                    if i==0:

                        start_time=0.0001

                    else:

                        start_time = i/frame_rate

                    current_stable_frames.append(frames[i])

                else:

                    current_stable_frames.append(frames[i])

            else:

                if len(current_stable_frames)>=required_stable_frames:

                    end_ind = i-1

                    end_time = (i-1)/frame_rate

                    print(f"Stable Frame Starts {start_time} and ends at {end_time}")

                    stable_frames.append(frames[i-1])

                    start_and_end.append((start_time,end_time))

                    cv2.imwrite(f"stable_frames/image_{stable_frames_count}.jpg",frames[i-1])

                else:

                    pass
                    
                    # print("Skipping.. :",len(current_stable_frames),"Required : ",required_stable_frames)

                start_time,end_time, start_ind, end_ind, current_stable_frames = None,None,None,None,[]

        if len(current_stable_frames)>=required_stable_frames:

            end_ind = i=i

            end_time = (i-1)/frame_rate

            stable_frames.append(frames[np.random.randint(start_ind+1,end_ind-1)])

            start_and_end.append((start_time,end_time))

        gc.collect()
        
        return stable_frames, start_and_end
    
    def extract_audio(self,audio_output_path="audio.mp3"):
        """
        Extracts audio from a video file and saves it to the specified output path.

        :param video_path: Path to the input video file.
        :param audio_output_path: Path to save the extracted audio file.
        """
        # Load the video file
        video = VideoFileClip(self.video_path)
        
        # Extract audio
        audio = video.audio
        
        # Write audio to file
        audio.write_audiofile(audio_output_path)
        
        # Close the video file
        video.close()

        print("Audio Extracted Successfully....")

    def split_audio_with_ffmpeg(self,audio_path="audio_chunk.wav", timestamps=[], output_dir="audio_segments"):
        """
        Splits an audio file based on given timestamps using FFmpeg and saves each segment.

        Parameters:
        - audio_path (str): Path to the original audio file.
        - timestamps (list of tuples): List of (start, end) timestamps in seconds for splitting.
        - output_dir (str): Directory to store split audio segments.

        Returns:
        - List of paths to the saved audio segments.
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        transcriptions = []

        for i, (_, end) in enumerate(timestamps):

            if not len(transcriptions):
                start = 0

            # Define the output path for the segment
            segment_path = os.path.join(output_dir, audio_path)

            if len(timestamps)==i:

                (
                ffmpeg
                .input(audio_path, ss=start,)
                .output(segment_path)
                .run(quiet=True, overwrite_output=True)
                )
            else:
                (
                    ffmpeg
                    .input(audio_path, ss=start, to=end)
                    .output(segment_path)
                    .run(quiet=True, overwrite_output=True)
                )

            text = [i[2] for i in self.transcribe_audio(segment_path)]

            final_text = "\n".join(text) if len(text)>1 else text[0]

            transcriptions.append(final_text)

            start = end

        return transcriptions

            
    def transcribe_audio(self,file_path="audio.mp3"):

        segments, info = self.__transcription_model.transcribe(file_path, beam_size=5, language="en", condition_on_previous_text=False)
        
        transcripton = []

        for segment in segments:
            
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

            transcripton.append((segment.start, segment.end, segment.text))

        return transcripton


    def map_frames_and_transcription(self,start_and_end_frame,transcripton):
        
        final_transcription = []

        starting_list = [i[0] for i in transcripton]
        ending_list = [i[1] for i in transcripton]
        text_list = [i[2] for i in transcripton]

        start = 0

        for _, end in start_and_end_frame:

            # Find closest index in starting_list to start
            closest_start_index = min(enumerate(starting_list), key=lambda x: abs(x[1] - start))[0]

            # Find closest index in ending_list to end
            closest_end_index = min(enumerate(ending_list), key=lambda x: abs(x[1] - end))[0]

            start = ending_list[closest_end_index]

            if not len(final_transcription):

                closest_start_index = 0

            final_transcription.append("\n".join(text_list[closest_start_index:closest_end_index+1]).strip())

        return final_transcription


    def get_frames_and_time(self):

        print("***************** Extracting Frames From the Video *****************************")
        frames,frame_rate = self.extract_video_frames()
        print(f"Extracted {len(frames)} frames.")
        print("***************** Finding The Stable Frames From The Video **********************")
        stable_frames, start_and_end_frame = self.find_stable_frames(frames, frame_rate)
        # print("***************** Transcribing The Audio ****************************")
        self.extract_audio()
        transcripton = self.transcribe_audio()
        final_text = self.map_frames_and_transcription(start_and_end_frame,transcripton)
        # transcripton = self.split_audio_with_ffmpeg("audio.mp3",start_and_end_frame)
        create_blog_post(self.title,stable_frames,final_text)
        gc.collect()

        return "blog_post/centered_blog_post.html"
        # return start_and_end_frame,transcripton
        
# video_path = r"samples\videoplayback.mp4"

# model = VideoToBlog(video_path,"K-Means Clustering",stable_duration_sec=3)

# model.get_frames_and_time()
