import os
import sys
import srt
from gtts import gTTS
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip

def find_files():
    # Get the folder where the script is currently running
    current_dir = os.getcwd()
    print(f"Scanning folder: {current_dir}\n")

    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv')
    video_file = None
    srt_file = None

    # Scan the directory for the first matching video and srt file
    for file in os.listdir(current_dir):
        if file.lower().endswith(video_extensions) and not file.startswith('output_'):
            video_file = file
        elif file.lower().endswith('.srt'):
            srt_file = file

    return video_file, srt_file

def parse_srt_to_audio_clips(srt_path):
    print(f"Parsing '{srt_path}' and generating robotic voice clips...")
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_data = f.read()
    
    subtitles = list(srt.parse(srt_data))
    audio_clips = []
    temp_files = []
    
    for i, sub in enumerate(subtitles):
        if not sub.content.strip():
            continue
            
        temp_filename = f"temp_sub_{i}.mp3"
        temp_files.append(temp_filename)
        
        # Generate robotic TTS voice
        tts = gTTS(text=sub.content, lang='en', slow=False)
        tts.save(temp_filename)
        
        # Set the timeline start based on the SRT timestamp
        start_seconds = sub.start.total_seconds()
        clip = AudioFileClip(temp_filename).set_start(start_seconds)
        audio_clips.append(clip)
        
    return audio_clips, temp_files

def merge_srt_audio_with_video(video_path, srt_path, output_video_path):
    temp_files = []
    video_clip = None
    
    try:
        video_clip = VideoFileClip(video_path)
        tts_audio_clips, temp_files = parse_srt_to_audio_clips(srt_path)
        
        if not tts_audio_clips:
            print("No valid subtitles found in the SRT file.")
            return

        print("Mixing audio layers and syncing with video timeline...")
        combined_tts_audio = CompositeAudioClip(tts_audio_clips)
        
        final_video = video_clip.set_audio(combined_tts_audio)
        
        print(f"Rendering final video to '{output_video_path}'...")
        final_video.write_videofile(
            output_video_path, 
            codec="libx264", 
            audio_codec="aac",
            fps=video_clip.fps
        )
        print(f"\nSuccess! Process complete.")
        
    finally:
        if video_clip:
            video_clip.close()
        
        print("Cleaning up temporary audio files...")
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"Could not remove temporary file {file}: {e}")

if __name__ == "__main__":
    # Automatically look for files in the current directory
    video_file, srt_file = find_files()

    if not video_file:
        print("Error: No video file (.mp4, .mkv, .avi) found in this folder.")
        sys.exit()
    if not srt_file:
        print("Error: No .srt subtitle file found in this folder.")
        sys.exit()

    print(f"Found Video : {video_file}")
    print(f"Found SRT   : {srt_file}")
    print("-" * 40)

    output_name = f"output_{video_file}"
    
    merge_srt_audio_with_video(video_file, srt_file, output_name)