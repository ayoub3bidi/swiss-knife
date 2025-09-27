# Audio Conversion Tools

Collection of Python scripts for audio and video conversion tasks. These tools provide simple command-line interfaces for common media processing operations.

## Scripts Overview

### batch_image_converter.py
Resize and convert images between multiple formats (JPEG, PNG, WebP, BMP, TIFF, GIF) with batch processing and advanced resizing modes.

**Features:**
- Multi-format conversion: JPEG, PNG, WebP, BMP, TIFF, GIF
- Flexible resizing: fit, fill, stretch, pad modes
- Quality presets for lossy formats
- Batch processing with glob patterns and directories
- Parallel processing for faster conversions
- EXIF metadata preservation
- Auto-orientation based on EXIF data
- Background color options for padding
- Comprehensive error handling and recovery

**Usage:**
```bash
python batch_image_converter.py --width 800 --height 600 *.jpg
python batch_image_converter.py --format webp --quality high ~/Pictures
python batch_image_converter.py --width 1920 --mode fit --output ./resized *.png
```

**Resize Modes:**
- `fit`: Resize to fit within dimensions, preserve aspect ratio (default)
- `fill`: Fill exact dimensions, crop if necessary
- `stretch`: Stretch to exact dimensions, ignore aspect ratio
- `pad`: Pad with background color to fit exact dimensions

**Quality Settings:**
- `low`: 60% quality for JPEG/WebP
- `medium`: 80% quality (default)
- `high`: 95% quality
- `maximum`: 100% quality, no optimization

**Advanced Options:**
```bash
# Parallel processing with custom background
python batch_image_converter.py --width 500 --mode pad --background "#ff0000" --workers 8 photos/

# Format conversion with EXIF preservation
python batch_image_converter.py --format jpeg --quality high --no-auto-orient images/

# Batch resize with overwrite
python batch_image_converter.py --height 1080 --overwrite --verbose ~/Pictures/
```

### batch_audio_converter.py
Converts audio files between multiple formats (MP3, WAV, OGG, FLAC) with batch processing and quality control.

**Features:**
- Multi-format conversion: MP3, WAV, OGG, FLAC
- Quality presets: low, medium, high, lossless
- Batch processing with glob patterns and directories
- Parallel processing for faster conversions
- Progress tracking with real-time statistics
- Compression ratio calculation
- Comprehensive error handling and recovery
- Configurable output directory

**Usage:**
```bash
python batch_audio_converter.py --format mp3 *.wav
python batch_audio_converter.py --format flac --quality high ~/Music
python batch_audio_converter.py --format ogg --output ./converted music.mp3 audio.wav
```

**Quality Settings:**
- `low`: 128k bitrate for MP3, optimized for storage
- `medium`: 192k bitrate (default), balanced quality/size
- `high`: 320k bitrate, maximum lossy quality
- `lossless`: No compression for FLAC/WAV

**Advanced Options:**
```bash
# Parallel processing with 8 threads
python batch_audio_converter.py --format mp3 --workers 8 ~/audio/

# Overwrite existing files
python batch_audio_converter.py --format wav --overwrite *.mp3

# Verbose logging
python batch_audio_converter.py --format flac --verbose music/
```

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

### batch_image_converter.py Implementation
- **Multi-threading**: Parallel image processing using ThreadPoolExecutor
- **Format Detection**: Automatic image file discovery with extension filtering
- **EXIF Handling**: Preserve metadata and auto-rotate based on orientation tags
- **Memory Optimization**: Individual file processing to handle large batches
- **Quality Control**: Format-specific optimization and compression settings
- **Color Mode Conversion**: Automatic mode conversion (RGBA→RGB, etc.)

#### Image Processing Pipeline
- **Load**: Open image with PIL, detect format and color mode
- **Orient**: Auto-rotate based on EXIF orientation data
- **Resize**: Apply selected resize mode with high-quality resampling
- **Convert**: Change color mode if required by target format
- **Save**: Export with format-specific quality settings and metadata

#### Resize Algorithms
- **Fit**: Thumbnail resize preserving aspect ratio within bounds
- **Fill**: Crop to fill exact dimensions using ImageOps.fit
- **Stretch**: Direct resize ignoring aspect ratio
- **Pad**: Center image on colored background to exact dimensions

### batch_audio_converter.py Implementation
- **Multi-threading**: Parallel conversion using ThreadPoolExecutor
- **Format Detection**: Automatic audio file discovery with extension filtering
- **Quality Control**: Preset-based bitrate and codec parameter management
- **Error Recovery**: Individual file failure doesn't stop batch processing
- **Memory Efficiency**: Processes files individually to handle large batches
- **Progress Tracking**: Real-time statistics with tqdm integration

#### Conversion Parameters
- **MP3**: Variable bitrate encoding with quality presets
- **FLAC**: Lossless compression with configurable compression level
- **OGG**: Vorbis codec with quality-based encoding
- **WAV**: Uncompressed PCM audio

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

All scripts include comprehensive error handling:
- File existence verification
- Format validation and codec support detection
- Exception catching with user-friendly messages
- Automatic cleanup of temporary files
- Clear success/failure feedback with detailed error reporting
- Graceful handling of corrupted or unsupported files

## Performance Notes

### batch_audio_converter.py
- Parallel processing scales with CPU cores
- Memory usage remains constant regardless of batch size
- Supports interruption and resume capabilities
- Progress tracking includes throughput metrics

### wav_to_mp3.py
- Fast conversion for typical file sizes
- Memory efficient for large files
- No temporary file creation

### sound_to_video.py
- Processing time depends on audio duration
- Memory usage scales with file length
- Temporary files created during processing
- Progress indicators for long operations

## Usage Examples

### Basic Conversions
```bash
# Single file conversions
python wav_to_mp3.py audio.wav
python sound_to_video.py music.mp3

# Batch format conversion
python batch_audio_converter.py --format mp3 *.wav
python batch_audio_converter.py --format flac ~/Music/
```

### Advanced Batch Processing
```bash
# High-quality conversion with custom output
python batch_audio_converter.py --format flac --quality lossless --output ./converted ~/audio/

# Fast parallel processing
python batch_audio_converter.py --format mp3 --quality low --workers 8 --overwrite ./music/

# Mixed format batch conversion
python batch_audio_converter.py --format ogg file1.mp3 file2.wav dir1/ "*.flac"
```

### Integration Examples
```bash
# Convert and visualize workflow
python batch_audio_converter.py --format wav audio/*.mp3
python sound_to_video.py audio/music.wav
```

## Limitations

### batch_audio_converter.py
- Output format must be different from input format
- Thread count limited by system resources
- Large batch operations may require significant disk space

### wav_to_mp3.py
- Input must be valid WAV format
- No quality/bitrate configuration
- Single file processing only

### sound_to_video.py
- Large audio files may require significant processing time
- Output video size depends on audio duration
- Fixed visualization style (waveform only)
- No customization options for colors/layout

## Future Improvements

- [ ] Add metadata preservation during conversion
- [ ] Implement audio normalization options
- [ ] Add support for embedded album art
- [ ] Create configuration file support for batch operations
- [ ] Add multiple visualization styles for video generation
- [ ] Implement resume capability for interrupted batch operations
- [ ] Add audio analysis and quality metrics
- [ ] Support for custom FFmpeg parameters
- [ ] Integration with music library management
- [ ] Web-based batch conversion interface
