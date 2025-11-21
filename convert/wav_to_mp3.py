import os
import sys

from pydub import AudioSegment


def convert_wav_to_mp3(wav_path):
    try:
        if not os.path.exists(wav_path):
            print(f"Error: File '{wav_path}' does not exist.")
            return False

        if not wav_path.lower().endswith(".wav"):
            print("Error: File must be a .wav file")
            return False

        directory = os.path.dirname(wav_path)
        filename = os.path.splitext(os.path.basename(wav_path))[0]

        mp3_path = os.path.join(directory, f"{filename}.mp3")

        print(f"Converting {wav_path} to MP3...")
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format="mp3")

        print(f"Successfully converted! Saved as: {mp3_path}")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_wav_file>")
        sys.exit(1)

    wav_path = sys.argv[1]
    convert_wav_to_mp3(wav_path)


if __name__ == "__main__":
    main()
