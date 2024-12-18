from googleapiclient.discovery import build
import re
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip,AudioFileClip
import yt_dlp
import os
import cv2
import pysrt
import textwrap
import assemblyai as aai
api_key = 'AIzaSyDoVkEyPUdD6OUW-Dr_2pfbJhgU7hUtG-s'
video_url = 'https://www.youtube.com/watch?v=jAqsAVIz3Qs'
db = {}
youtube = build('youtube', 'v3', developerKey=api_key)
import shutil


def create_zip_file(Folder):
    folder_path = Folder

    # Path where the ZIP file will be created (without .zip extension)
    zip_file_path = Folder

    # Create a ZIP file
    shutil.make_archive(zip_file_path, 'zip', folder_path)
class VideoClip():
    def __init__(self, video_url,no_of_comments):
        self.video_url = video_url
        self.no_of_comments = no_of_comments



    def get_video_clip(self):
        def add_subtitles(input_video):
            aai.settings.api_key = "3d55134d8f7d4d6fa7c5b408a14165f5"

            # You can also transcribe a local file by passing in a file path
            # FILE_URL = './path/to/file.mp3'

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(f'{input_video}.mp4')

            if transcript.status == aai.TranscriptStatus.error:
                print(transcript.error)
            else:
                print(transcript.text)
                subtitles = transcript.export_subtitles_srt()
                print(subtitles)
                f = open(f'subtitles_{input_video}.srt', 'a')
                f.write(subtitles)
                f.close()
            def parse_srt(srt_file):
                subtitles = pysrt.open(srt_file)
                parsed_subs = []

                for sub in subtitles:
                    parsed_subs.append({
                        'start': sub.start.ordinal,
                        'end': sub.end.ordinal,
                        'text': sub.text.replace('\n', ' ')
                    })

                return parsed_subs

            def add_subtitles_to_frame(frame, text, position, font, font_scale, font_color, font_thickness,
                                       max_chars_per_line=40):
                wrapped_text = textwrap.wrap(text, width=max_chars_per_line)
                y = position[1]

                for line in wrapped_text:
                    text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
                    text_x = (frame.shape[1] - text_size[0]) // 2  # Center horizontally
                    text_y = y  # Vertical position
                    cv2.putText(
                        frame,
                        line,
                        (text_x, text_y),
                        font,
                        font_scale,
                        font_color,
                        font_thickness,
                        cv2.LINE_AA
                    )
                    y += text_size[1] + 10  # Move to the next line, with some spacing

                return frame

            def burn_subtitles(input_video, output_video, subtitles):
                cap = cv2.VideoCapture(input_video)
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

                font = cv2.FONT_HERSHEY_COMPLEX
                font_scale = 0.5
                font_color = (0, 0, 255)  # Red color in BGR
                font_thickness = 1
                outline_color = (0, 0, 0)  # Black outline color
                outline_thickness = 2

                current_sub_idx = 0
                num_subs = len(subtitles)

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC))

                    if current_sub_idx < num_subs and subtitles[current_sub_idx]['start'] <= current_time <= \
                            subtitles[current_sub_idx]['end']:
                        text = subtitles[current_sub_idx]['text']

                        frame = add_subtitles_to_frame(frame, text, (width // 2, height // 2), font, font_scale,
                                                       outline_color, outline_thickness)
                        frame = add_subtitles_to_frame(frame, text, (width // 2, height // 2), font, font_scale,
                                                       font_color,
                                                       font_thickness)

                    if current_sub_idx < num_subs and current_time > subtitles[current_sub_idx]['end']:
                        current_sub_idx += 1

                    out.write(frame)

                cap.release()
                out.release()
                cv2.destroyAllWindows()

            def extract_audio(input_video, output_audio):
                video = VideoFileClip(input_video)
                video.audio.write_audiofile(output_audio)

            def add_audio_to_video(video_file, audio_file, output_file):
                video = VideoFileClip(video_file)
                audio = AudioFileClip(audio_file)
                final_video = video.set_audio(audio)
                final_video.write_videofile(output_file, codec='libx264')

            # Usage example

            srt_file = f'subtitles_{input_video}.srt'
            temp_output_video = f'{input_video}_with_subtitles.avi'
            output_video = f'{input_video}_with_subtitles.mp4'
            output_audio = 'extracted_audio.mp3'

            subtitles = parse_srt(srt_file)
            burn_subtitles(f'{input_video}.mp4', temp_output_video, subtitles)
            extract_audio(f'{input_video}.mp4', output_audio)
            add_audio_to_video(temp_output_video, output_audio, output_video)


        def extract_video_id_from_url(url):
            if 'youtu.be/' in url:
                video_id = url.split('/')[-1]
            else:
                video_id = url.split('v=')[1].split('&')[0]

            return video_id

        def download_youtube_video(video_url, save_path="."):
            ydl_opts = {
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',  # Save as title.extension
                'format': 'best',  # Get the best video and audio quality
                'cookiefile': 'cookies.txt'
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract video information
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_title = info_dict.get('title', 'video')  # Get the video title
                    video_ext = info_dict.get('ext', 'mp4')  # Get the video extension

                    # Construct the full path to the downloaded file
                    video_path = os.path.join(save_path, fr"{video_title}.{video_ext}")

                    print("Download completed successfully!")
                    return video_path
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        def get_comments(youtube, video_id):
            # Call the commentThreads.list method to retrieve comments
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=self.no_of_comments,  # Change this value to get more or fewer comments
                textFormat='plainText'
            )
            response = request.execute()

            comments = []
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            return comments

        def contains_timestamp(comment):
            # Regular expression to match typical timestamp patterns like "1:23", "10:45", etc.
            timestamp_pattern = re.compile(r'\b\d{1,2}:\d{2}\b')
            return bool(timestamp_pattern.search(comment))

        def extract_timestamps(comment):
            # Regular expression to match typical timestamp patterns like "1:23", "10:45", "01:23:45", etc.
            timestamp_pattern = re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b')
            timestamps = timestamp_pattern.findall(comment)
            return timestamps
        def add_seconds_to_timestamp(timestamp, seconds):
            if len(timestamp.split(':')) == 2:
                # Format: MM:SS
                time_format = '%M:%S'
            else:
                # Format: HH:MM:SS
                time_format = '%H:%M:%S'

            # Parse the timestamp into a datetime object
            time_obj = datetime.strptime(timestamp, time_format)
            # Add the seconds
            new_time_obj = time_obj + timedelta(seconds=seconds)

            # Format the new datetime object back to a string
            if len(timestamp.split(':')) == 2:
                return new_time_obj.strftime('%M:%S')
            else:
                return new_time_obj.strftime('%H:%M:%S')


        def time_to_seconds(time_str):
            # Regular expression to match time in the format HH:MM:SS or MM:SS
            time_pattern = re.compile(r'(\d+):(\d+)(?::(\d+))?')
            match = time_pattern.match(time_str)

            if match:
                hours, minutes, seconds = match.groups()
                if seconds is None:
                    seconds = 0
                return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds)
            else:
                raise ValueError(f"Invalid time format: {time_str}")
        # Fetch and print comments

        def extract_clips(video_path, clips):
            # Load the video
            video = VideoFileClip(video_path)

            for idx, (clip_name, times) in enumerate(clips.items()):
                start_time = times['start']
                end_time = times['end']

                # Extract the subclip
                clip = video.subclip(start_time, end_time)

                target_width = 720  # Example width for shorts format
                target_height = 1280  # Example height for shorts format

                # Resize the video while preserving aspect ratio
                  # Use BILINEAR method

                # Define the output file path
                output_file = f'Final_OGdim\clip_{idx + 1}.mp4'

                # Write the resized subclip to a file
                clip.write_videofile(output_file, codec='libx264')


        def resize_and_add_audio(input_video_path, output_video_path, target_width, target_height):
            # Extract the audio from the input video
            def extract_audio_from_video(source_video_path, audio_output_path):
                video = VideoFileClip(source_video_path)
                audio = video.audio
                audio.write_audiofile(audio_output_path)
                video.close()

            # Resize the video
            def resize_video(input_video_path, output_video_path, target_width, target_height):
                cap = cv2.VideoCapture(input_video_path)

                if not cap.isOpened():
                    print(f"Error: Video file not found at {input_video_path}")
                    return False

                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"Original video dimensions: {frame_width}x{frame_height}")

                if frame_width <= 0 or frame_height <= 0 or target_width <= 0 or target_height <= 0:
                    print("Error: Video frame dimensions and target dimensions must be positive")
                    return False

                new_width = int(target_width)
                new_height = int(target_height)
                print(f"New video dimensions: {new_width}x{new_height}")

                out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), cap.get(cv2.CAP_PROP_FPS),
                                      (new_width, new_height))

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized_frame = cv2.resize(frame, (new_width, new_height))
                    out.write(resized_frame)

                cap.release()
                out.release()
                return True

            # Add the extracted audio to the resized video
            def add_audio_to_video(target_video_path, audio_input_path, output_video_path):
                video = VideoFileClip(target_video_path)
                audio = AudioFileClip(audio_input_path)
                video = video.set_audio(audio)
                video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
                video.close()
                audio.close()

            audio_path = "extracted_audio.mp3"
            resized_video_path = "resized_video.mp4"

            # Extract audio
            extract_audio_from_video(input_video_path, audio_path)

            # Resize video
            if resize_video(input_video_path, resized_video_path, target_width, target_height):
                # Add audio to resized video
                add_audio_to_video(resized_video_path, audio_path, output_video_path)
                print("Video resizing and audio processing completed successfully.")
            else:
                print("Failed to resize the video.")
        video_id = extract_video_id_from_url(self.video_url)
        comments = get_comments(youtube, video_id)
        clip_no = 0
        try:
            for idx, comment in enumerate(comments):
                timestamps = extract_timestamps(comment)
                if timestamps:
                    print(f"Comment {idx + 1}: {comment}")
                    clip_no = clip_no + 1
                    for timestamp in timestamps:
                        print(f"  Extracted timestamp: {timestamp}")
                        print(f"  End Time stamp: {add_seconds_to_timestamp(timestamp,15)}")
                        db[f"Clip {clip_no}"] = {"start": timestamp, "end": add_seconds_to_timestamp(timestamp,15)}
                else:
                    continue
        except Exception as e:
            print(f"Error: {e}")
            pass

        print(db)

        video_path = download_youtube_video(self.video_url,fr"{os.getcwd()}")
        print(video_path)
        extract_clips(video_path, db)
        for i in range(len(db)):
            resize_and_add_audio(f'Final_OGdim\clip_{i+1}.mp4',f'Final_Resize\clip{i+1}_final.mp4',360,450)
            #add_subtitles(f'clip{i+1}_final')


#videdit = VideoClip('https://www.youtube.com/watch?v=RKtl_L4ASQ4',100)
#videdit.get_video_clip()
