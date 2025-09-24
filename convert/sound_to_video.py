import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.io import wavfile
import moviepy.editor as mpe
from pydub import AudioSegment
import tempfile
import matplotlib
matplotlib.use('Agg')  #! Required for saving animation
# from tqdm import tqdm

def convert_to_wav(audio_path):
    try:
        print(f"Converting {audio_path} to WAV format...")
        audio = AudioSegment.from_file(audio_path)

        temp_dir = tempfile.gettempdir()
        temp_wav = os.path.join(temp_dir, "temp_audio_conversion.wav")

        audio.export(temp_wav, format="wav")
        return temp_wav
    except Exception as e:
        print(f"Error converting audio file: {str(e)}")
        return None

def create_audio_visualization(audio_path):
    try:
        if not os.path.exists(audio_path):
            print(f"Error: File '{audio_path}' does not exist.")
            return False

        directory = os.path.dirname(audio_path) if os.path.dirname(audio_path) else '.'
        filename = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = os.path.join(directory, f"{filename}_visualization.mp4")

        temp_wav = None
        if not audio_path.lower().endswith('.wav'):
            temp_wav = convert_to_wav(audio_path)
            if not temp_wav:
                return False
            wav_path = temp_wav
        else:
            wav_path = audio_path

        print("Reading audio file...")
        sample_rate, audio_data = wavfile.read(wav_path)

        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        duration = len(audio_data) / sample_rate

        segment_duration = 0.05  # 50ms segments
        segment_samples = int(sample_rate * segment_duration)
        num_segments = len(audio_data) // segment_samples

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        line, = ax.plot([], [], lw=2, color='cyan')

        max_amplitude = np.max(np.abs(audio_data))
        ax.set_xlim(0, segment_samples)
        ax.set_ylim(-max_amplitude, max_amplitude)
        ax.set_xticks([])
        ax.set_yticks([])

        def animate(frame):
            start_idx = frame * segment_samples
            end_idx = start_idx + segment_samples
            segment = audio_data[start_idx:end_idx]
            line.set_data(range(len(segment)), segment)
            return line,

        print("Creating animation...")
        anim = FuncAnimation(fig, animate, frames=num_segments,
                           interval=segment_duration*1000, blit=True)

        temp_path = "temp_animation.mp4"
        anim.save(temp_path, fps=int(1/segment_duration), 
                 progress_callback=lambda i, n: print(f'Saving frame {i} of {n}'))
        plt.close()

        print("Adding audio to video...")
        video = mpe.VideoFileClip(temp_path)
        audio = mpe.AudioFileClip(audio_path)
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_path, codec='libx264', 
                                  audio_codec='aac', fps=int(1/segment_duration))

        os.remove(temp_path)
        if temp_wav:
            os.remove(temp_wav)
        
        print(f"Successfully created visualization! Saved as: {output_path}")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if os.path.exists("temp_animation.mp4"):
            os.remove("temp_animation.mp4")
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python audio_to_video.py <path_to_audio_file>")
        print("Supported formats: MP3, WAV, OGG, FLAC, AAC, M4A, WMA, and more")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    create_audio_visualization(audio_path)

if __name__ == "__main__":
    main()