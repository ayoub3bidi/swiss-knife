import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('Agg')
from scipy.io import wavfile
import moviepy.editor as mpe
from pydub import AudioSegment
import tempfile
from tqdm import tqdm
import argparse
from PIL import Image
import textwrap
from datetime import timedelta
import psutil
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

class ThermalMonitor:
    def __init__(self, threshold_temp=75):
        self.threshold_temp = threshold_temp
        self.warning_temp = threshold_temp - 5
        self.check_interval = 1  # seconds
        self.running = True
        self._start_monitoring()

    def _start_monitoring(self):
        self.monitor_thread = ThreadPoolExecutor(max_workers=1)
        self.future = self.monitor_thread.submit(self._monitor_loop)

    def _get_cpu_temperature(self):
        try:
            # Try to get temperature on Linux systems
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000
            return temp
        except:
            try:
                # Try using psutil for other systems
                temperatures = psutil.sensors_temperatures()
                if temperatures:
                    # Get the highest temperature from any sensor
                    return max(temp.current for sensor in temperatures.values() 
                             for temp in sensor)
            except:
                return None
        return None

    def _monitor_loop(self):
        while self.running:
            temp = self._get_cpu_temperature()
            if temp is not None:
                if temp >= self.threshold_temp:
                    print(f"\n⚠️ WARNING: CPU temperature ({temp}°C) exceeded threshold! Pausing processing...")
                    raise RuntimeError(f"Temperature threshold exceeded: {temp}°C")
                elif temp >= self.warning_temp:
                    print(f"\n⚠️ High CPU temperature: {temp}°C")
            time.sleep(self.check_interval)

    def stop(self):
        self.running = False
        self.monitor_thread.shutdown(wait=False)

class PodcastVisualizer:
    def __init__(self, audio_path, **kwargs):
        self.audio_path = audio_path
        self.temp_files = []
        
        # Default settings with resource optimization
        self.settings = {
            'width': 1920,
            'height': 1080,
            'background_color': 'black',
            'waveform_color': '#00ffff',
            'secondary_color': '#ff00ff',
            'title': None,
            'episode_number': None,
            'background_image': None,
            'output_format': 'mp4',
            'visualization_style': 'wave',
            'segment_duration': 0.05,
            'quality': 'medium',  # Default to medium for better performance
            'add_timestamp': True,
            'add_progress_bar': True,
            'logo_path': None,
            'max_threads': max(1, multiprocessing.cpu_count() - 1),  # Leave one CPU core free
            'batch_size': 100,  # Number of frames to process in one batch
            'temperature_threshold': 75  # Celsius
        }
        
        # Update settings with any provided kwargs
        self.settings.update(kwargs)
        
        # Quality presets optimized for performance
        self.quality_presets = {
            'low': {'fps': 24, 'dpi': 100, 'downscale': 0.75},
            'medium': {'fps': 30, 'dpi': 150, 'downscale': 1.0},
            'high': {'fps': 60, 'dpi': 200, 'downscale': 1.0}
        }

        # Initialize thermal monitor
        self.thermal_monitor = ThermalMonitor(self.settings['temperature_threshold'])

    def process_frame_batch(self, batch_data):
        """Process a batch of frames to reduce memory usage"""
        frames_data, temp_dir, start_frame = batch_data
        results = []
        
        for i, frame in enumerate(frames_data):
            frame_number = start_frame + i
            try:
                fig = self.create_visualization_frame(
                    self.audio_data, frame_number, 
                    self.segment_samples, self.max_amplitude
                )
                frame_path = os.path.join(temp_dir, f"frame_{frame_number:06d}.png")
                
                # Optimize figure saving
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fig.savefig(frame_path, bbox_inches='tight', pad_inches=0, 
                              dpi=self.quality_presets[self.settings['quality']]['dpi'])
                plt.close(fig)
                results.append(frame_path)
                
            except Exception as e:
                print(f"Error processing frame {frame_number}: {str(e)}")
                
            # Add small delay to prevent CPU overheating
            time.sleep(0.01)
        
        return results

    def create_visualization(self):
        try:
            # Convert to WAV if needed
            wav_path = self.convert_to_wav()
            
            print("Reading audio file...")
            self.sample_rate, self.audio_data = wavfile.read(wav_path)
            
            # Convert stereo to mono if necessary
            if len(self.audio_data.shape) > 1:
                self.audio_data = self.audio_data.mean(axis=1)

            # Calculate segments
            self.segment_samples = int(self.sample_rate * self.settings['segment_duration'])
            num_segments = len(self.audio_data) // self.segment_samples
            self.max_amplitude = np.max(np.abs(self.audio_data)) * 1.1

            # Create temporary directory for frames
            temp_dir = tempfile.mkdtemp()
            self.temp_files.append(temp_dir)

            # Process frames in batches using multiple threads
            print("Generating frames...")
            batch_size = self.settings['batch_size']
            num_batches = (num_segments + batch_size - 1) // batch_size

            with ThreadPoolExecutor(max_workers=self.settings['max_threads']) as executor:
                futures = []
                
                for i in range(num_batches):
                    start_frame = i * batch_size
                    end_frame = min(start_frame + batch_size, num_segments)
                    batch_frames = range(start_frame, end_frame)
                    
                    future = executor.submit(
                        self.process_frame_batch, 
                        (batch_frames, temp_dir, start_frame)
                    )
                    futures.append(future)

                # Process results with progress bar
                with tqdm(total=num_segments) as pbar:
                    for future in as_completed(futures):
                        try:
                            results = future.result()
                            pbar.update(len(results))
                        except Exception as e:
                            print(f"\nError in batch processing: {str(e)}")
                            self.thermal_monitor.stop()
                            return False

            # Set up output path
            output_dir = os.path.dirname(self.audio_path) if os.path.dirname(self.audio_path) else '.'
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.audio_path))[0]
            output_path = os.path.join(output_dir, f"{filename}_visualization.{self.settings['output_format']}")

            # Combine frames into video with optimized settings
            print("Creating video...")
            fps = self.quality_presets[self.settings['quality']]['fps']
            frame_clip = mpe.ImageSequenceClip(temp_dir, fps=fps)
            
            # Add audio
            audio_clip = mpe.AudioFileClip(self.audio_path)
            final_clip = frame_clip.set_audio(audio_clip)
            
            # Write final video with optimized settings
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=fps,
                threads=self.settings['max_threads'],
                preset='medium'  # Balance between speed and quality
            )
            
            print(f"Successfully created visualization! Saved as: {output_path}")
            return True

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False
            
        finally:
            # Clean up
            self.thermal_monitor.stop()
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    if os.path.isdir(temp_file):
                        import shutil
                        shutil.rmtree(temp_file)
                    else:
                        os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description='Create video visualization from podcast audio.')
    parser.add_argument('audio_path', help='Path to the audio file')
    parser.add_argument('--title', help='Podcast title')
    parser.add_argument('--episode', help='Episode number')
    parser.add_argument('--style', choices=['wave', 'circle', 'bars'], default='wave',
                       help='Visualization style')
    parser.add_argument('--quality', choices=['low', 'medium', 'high'], default='medium',
                       help='Output quality')
    parser.add_argument('--background', help='Path to background image')
    parser.add_argument('--logo', help='Path to logo image')
    parser.add_argument('--color', help='Waveform color (hex code)', default='#00ffff')
    parser.add_argument('--max-temp', type=float, default=75.0,
                       help='Maximum CPU temperature threshold in Celsius')
    parser.add_argument('--threads', type=int, 
                       default=max(1, multiprocessing.cpu_count() - 1),
                       help='Number of processing threads')
    args = parser.parse_args()

    visualizer = PodcastVisualizer(
        args.audio_path,
        title=args.title,
        episode_number=args.episode,
        visualization_style=args.style,
        quality=args.quality,
        background_image=args.background,
        logo_path=args.logo,
        waveform_color=args.color,
        max_threads=args.threads,
        temperature_threshold=args.max_temp
    )
    visualizer.create_visualization()

if __name__ == "__main__":
    main()
