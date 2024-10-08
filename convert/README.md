# Converters

## WAV to MP3 Converter

A simple Python script to convert WAV audio files to MP3 format. The script maintains the original audio quality and saves the converted file in the same directory as the input file.

### Features

- Convert WAV files to MP3 format
- Maintains original audio quality
- Saves output in the same directory as input
- Simple command-line interface
- Error handling and validation

### Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6 or higher
- pip (Python package installer)
- ffmpeg (required for audio processing)

### Installation

2. Install ffmpeg (required for audio processing):
```bash
sudo apt update
sudo apt install ffmpeg
```

3. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

4. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Usage

1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

2. Run the script with a WAV file path as an argument:
```bash
python wav_to_mp3.py path/to/your/audio.wav
```

The script will create an MP3 file with the same name in the same directory.

#### Example:
```bash
python wav_to_mp3.py ~/Music/mysong.wav
```
This will create `~/Music/mysong.mp3`

### Error Handling

The script includes error handling for common issues:
- Non-existent input files
- Invalid file formats
- Processing errors

If any error occurs, the script will display an appropriate error message.

### Project Structure

```
convert/
├── wav_to_mp3.py
├── requirements.txt
└── README.md
```

### Contributing

If you'd like to contribute to this project, please feel free to:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Troubleshooting

If you encounter the error "ffmpeg not found", ensure ffmpeg is properly installed:
```bash
ffmpeg -version
```

If ffmpeg is not installed or not found, install it using:
```bash
sudo apt update
sudo apt install ffmpeg
```

For other issues, please check:
1. Python version (`python --version`)
2. Virtual environment activation
3. All requirements are installed (`pip list`)

## Audio to Waveform Video Converter

This Python script creates a video visualization of audio waveforms from various audio file formats. The output is an MP4 video that shows an animated waveform synchronized with the original audio.

### Features

- Supports multiple audio formats (MP3, WAV, OGG, FLAC, AAC, M4A, WMA, etc.)
- Creates smooth waveform animations
- Synchronizes animation with original audio
- Customizable visualization parameters
- High-quality MP4 output
- Progress tracking during conversion
- Same-directory output with original file

### Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6 or higher
- pip (Python package installer)
- FFmpeg (required for video and audio processing)

### Installation

1. Install system dependencies:
```bash
sudo apt update
sudo apt install ffmpeg python3-tk
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Usage

1. Activate your virtual environment:
```bash
source venv/bin/activate
```

2. Run the script with an audio file path as an argument:
```bash
python audio_to_video.py path/to/your/audio.mp3
```

The script will create an MP4 file with the name pattern `[original_name]_visualization.mp4` in the same directory as the input file.

#### Examples:
```bash
# Convert MP3 file
python audio_to_video.py ~/Music/song.mp3

# Convert FLAC file
python audio_to_video.py ~/Music/song.flac

# Convert M4A file
python audio_to_video.py ~/Music/song.m4a
```

### Supported Audio Formats

The script supports all audio formats that FFmpeg can handle, including:
- MP3
- WAV
- OGG
- FLAC
- AAC
- M4A
- WMA
- And many more...

### Customization

You can modify these parameters in the script to customize the visualization:
- `segment_duration`: Controls how much audio is shown in each frame (default: 0.05 seconds)
- `figsize`: Controls the size of the video frame (default: 10x6)
- Line color and thickness in the `plot` function
- Background color using `set_facecolor`

### Troubleshooting

Common issues and solutions:

1. **Missing FFmpeg**:
```bash
sudo apt install ffmpeg
```

2. **TkInter errors**:
```bash
sudo apt install python3-tk
```

3. **Memory errors**: Reduce `segment_duration` value in the script for longer audio files

4. **Format not supported**: Update FFmpeg to latest version:
```bash
sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt update
sudo apt install ffmpeg
```

### Technical Details

The script works by:
1. Converting input audio to WAV format if necessary
2. Reading the audio data using scipy
3. Segmenting the audio data into small chunks
4. Creating an animated visualization using matplotlib
5. Combining the animation with the original audio using moviepy
6. Outputting a synchronized MP4 file
7. Cleaning up temporary files

### Performance Notes

- Processing time depends on:
  - Input audio length
  - Segment duration
  - Output frame rate
  - System specifications
- Memory usage scales with audio length
- Temporary files are created during processing and automatically cleaned up
- Format conversion may take additional time for non-WAV files
