# Audio Conversion Tools

Collection of Python scripts for audio and video conversion tasks. These tools provide simple command-line interfaces for common media processing operations.

## Scripts Overview

### wav_to_mp3.py
Converts WAV audio files to MP3 format with error handling and validation.

**Features:**
- File existence validation
- Format verification (.wav extension check)
- Automatic output path generation
- Comprehensive error handling
- Progress feedback

**Usage:**
```bash
python wav_to_mp3.py input_file.wav
```

**Example:**
```bash
python wav_to_mp3.py audio/song.wav
# Output: audio/song.mp3
```

### sound_to_video.py
Creates animated audio visualizations by converting any audio file into a video with waveform animation.

**Features:**
- Multi-format audio support (MP3, WAV, OGG, FLAC, AAC, M4A, WMA)
- Automatic format conversion to WAV for processing
- Real-time waveform visualization
- Configurable visualization parameters
- Original audio preservation in final video
- Temporary file cleanup

**Usage:**
```bash
python sound_to_video.py input_audio_file
```

**Examples:**
```bash
python sound_to_video.py music.mp3
# Output: music_visualization.mp4

python sound_to_video.py podcast.wav
# Output: podcast_visualization.mp4
```

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

**Required libraries:**
- `pydub` - Audio format conversion and processing
- `matplotlib` - Visualization and animation creation
- `scipy` - Audio file reading and signal processing
- `moviepy` - Video creation and audio synchronization
- `numpy` - Numerical operations for audio data
- `tqdm` - Progress bar display

## Technical Details

### wav_to_mp3.py Implementation
- Uses `pydub.AudioSegment` for reliable format conversion
- Preserves original file location for output
- Maintains audio quality during conversion
- Returns boolean success/failure status

### sound_to_video.py Implementation
- **Audio Processing**: Converts input to WAV format if necessary
- **Visualization**: Creates 50ms segments for smooth animation
- **Animation**: Uses matplotlib's FuncAnimation for waveform display
- **Video Creation**: Combines animation with original audio using MoviePy
- **Cleanup**: Removes temporary files automatically

#### Visualization Parameters
- Segment duration: 50ms (configurable)
- Video framerate: 20 FPS
- Background: Black with cyan waveform
- Resolution: 10x6 inches (1000x600 pixels)

## Error Handling

Both scripts include comprehensive error handling:
- File existence verification
- Format validation
- Exception catching with user-friendly messages
- Automatic cleanup of temporary files
- Clear success/failure feedback

## Performance Notes

### wav_to_mp3.py
- Fast conversion for typical file sizes
- Memory efficient for large files
- No temporary file creation

### sound_to_video.py
- Processing time depends on audio duration
- Memory usage scales with file length
- Temporary files created during processing
- Progress indicators for long operations

## Limitations

### wav_to_mp3.py
- Input must be valid WAV format
- No batch processing support
- No quality/bitrate configuration

### sound_to_video.py
- Large audio files may require significant processing time
- Output video size depends on audio duration
- Fixed visualization style (waveform only)
- No customization options for colors/layout

## Future Improvements

- [ ] Add batch processing support
- [ ] Implement quality/bitrate options
- [ ] Add configuration file support
- [ ] Create multiple visualization styles
- [ ] Add progress bars for all operations
- [ ] Implement parallel processing for batch operations
- [ ] Add output format options (different video codecs)
- [ ] Include audio normalization options
