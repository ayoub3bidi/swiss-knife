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

### Support

For support, please:
1. Check the existing issues in the repository
2. Create a new issue with a detailed description of your problem
3. Include your system information and any relevant error messages
