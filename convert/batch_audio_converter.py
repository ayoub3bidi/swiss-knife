#!/usr/bin/env python3
import sys
import argparse
import glob
from pathlib import Path
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from tqdm import tqdm


@dataclass
class ConversionResult:
    source_path: str
    target_path: str
    success: bool
    error_message: Optional[str] = None
    source_size: Optional[int] = None
    target_size: Optional[int] = None


class BatchAudioConverter:
    SUPPORTED_FORMATS = {
        'mp3': {'extension': '.mp3', 'codec': 'mp3'},
        'wav': {'extension': '.wav', 'codec': 'wav'},
        'ogg': {'extension': '.ogg', 'codec': 'ogg'},
        'flac': {'extension': '.flac', 'codec': 'flac'}
    }
    
    QUALITY_PRESETS = {
        'low': {'bitrate': '128k', 'parameters': ['-q:a', '9']},
        'medium': {'bitrate': '192k', 'parameters': ['-q:a', '5']},
        'high': {'bitrate': '320k', 'parameters': ['-q:a', '0']},
        'lossless': {'bitrate': None, 'parameters': []}
    }
    
    def __init__(self, target_format: str, quality: str = 'medium', 
                 output_dir: Optional[str] = None, overwrite: bool = False,
                 max_workers: int = 4):
        """
        Initialize the batch converter.
        
        Args:
            target_format: Output format (mp3, wav, ogg, flac)
            quality: Quality preset (low, medium, high, lossless)
            output_dir: Output directory (None = same as source)
            overwrite: Whether to overwrite existing files
            max_workers: Number of parallel conversion threads
        """
        if target_format.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {target_format}")
        
        if quality not in self.QUALITY_PRESETS:
            raise ValueError(f"Invalid quality: {quality}")
        
        self.target_format = target_format.lower()
        self.quality = quality
        self.output_dir = Path(output_dir) if output_dir else None
        self.overwrite = overwrite
        self.max_workers = max_workers
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_output_path(self, source_path: Path) -> Path:
        target_ext = self.SUPPORTED_FORMATS[self.target_format]['extension']
        
        if self.output_dir:
            # Use specified output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return self.output_dir / f"{source_path.stem}{target_ext}"
        else:
            # Use same directory as source
            return source_path.parent / f"{source_path.stem}{target_ext}"
    
    def _convert_single_file(self, source_path: Path) -> ConversionResult:
        try:
            target_path = self._get_output_path(source_path)

            if target_path.exists() and not self.overwrite:
                return ConversionResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message="Target file exists (use --overwrite to replace)"
                )
            
            # Get source file size
            source_size = source_path.stat().st_size
            
            # Load audio file
            try:
                audio = AudioSegment.from_file(str(source_path))
            except CouldntDecodeError as e:
                return ConversionResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message=f"Could not decode audio file: {e}"
                )
            
            # Prepare export parameters
            export_params = {}
            quality_settings = self.QUALITY_PRESETS[self.quality]
            
            if self.target_format == 'mp3':
                if quality_settings['bitrate']:
                    export_params['bitrate'] = quality_settings['bitrate']
                export_params['parameters'] = quality_settings['parameters']
            elif self.target_format == 'ogg':
                export_params['parameters'] = quality_settings['parameters']
            
            # Convert and save
            audio.export(
                str(target_path),
                format=self.target_format,
                **export_params
            )
            
            # Get target file size
            target_size = target_path.stat().st_size
            
            return ConversionResult(
                source_path=str(source_path),
                target_path=str(target_path),
                success=True,
                source_size=source_size,
                target_size=target_size
            )
            
        except Exception as e:
            return ConversionResult(
                source_path=str(source_path),
                target_path=str(target_path) if 'target_path' in locals() else '',
                success=False,
                error_message=str(e)
            )
    
    def _find_audio_files(self, paths: List[str]) -> List[Path]:
        audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'}
        files = []
        
        for path_pattern in paths:
            # Handle glob patterns
            if '*' in path_pattern or '?' in path_pattern:
                matched_files = glob.glob(path_pattern)
                for file_path in matched_files:
                    p = Path(file_path)
                    if p.is_file() and p.suffix.lower() in audio_extensions:
                        files.append(p)
            else:
                path = Path(path_pattern)
                if path.is_file():
                    if path.suffix.lower() in audio_extensions:
                        files.append(path)
                elif path.is_dir():
                    # Recursively find audio files in directory
                    for ext in audio_extensions:
                        files.extend(path.rglob(f'*{ext}'))
                        files.extend(path.rglob(f'*{ext.upper()}'))
        
        # Remove duplicates and filter out files already in target format
        unique_files = []
        target_ext = self.SUPPORTED_FORMATS[self.target_format]['extension']
        
        for file_path in set(files):
            if file_path.suffix.lower() != target_ext:
                unique_files.append(file_path)
        
        return sorted(unique_files)
    
    def convert_batch(self, paths: List[str]) -> Dict[str, any]:
        # Find all audio files
        audio_files = self._find_audio_files(paths)
        
        if not audio_files:
            self.logger.warning("No audio files found for conversion")
            return {
                'total_files': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        self.logger.info(f"Found {len(audio_files)} files to convert to {self.target_format.upper()}")
        
        # Convert files with progress bar
        results = []
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_file = {
                executor.submit(self._convert_single_file, file_path): file_path 
                for file_path in audio_files
            }
            
            # Process completed conversions with progress bar
            with tqdm(total=len(audio_files), desc=f"Converting to {self.target_format.upper()}") as pbar:
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        successful += 1
                        # Calculate compression ratio if both sizes available
                        if result.source_size and result.target_size:
                            ratio = (result.target_size / result.source_size) * 100
                            pbar.set_postfix({
                                'Success': f"{successful}/{len(audio_files)}",
                                'Size': f"{ratio:.1f}%"
                            })
                    else:
                        failed += 1
                        self.logger.error(f"Failed to convert {result.source_path}: {result.error_message}")
                        pbar.set_postfix({
                            'Success': f"{successful}/{len(audio_files)}",
                            'Failed': failed
                        })
                    
                    pbar.update(1)
        
        # Calculate statistics
        total_source_size = sum(r.source_size for r in results if r.source_size)
        total_target_size = sum(r.target_size for r in results if r.target_size)
        
        stats = {
            'total_files': len(audio_files),
            'successful': successful,
            'failed': failed,
            'results': results,
            'total_source_size': total_source_size,
            'total_target_size': total_target_size,
            'compression_ratio': (total_target_size / total_source_size * 100) if total_source_size > 0 else 0
        }
        
        return stats
    
    def print_summary(self, stats: Dict[str, any]) -> None:
        print(f"\n{'='*50}")
        print("CONVERSION SUMMARY")
        print(f"{'='*50}")
        print(f"Total files processed: {stats['total_files']}")
        print(f"Successfully converted: {stats['successful']}")
        print(f"Failed conversions: {stats['failed']}")
        
        if stats['total_source_size'] > 0:
            source_mb = stats['total_source_size'] / (1024 * 1024)
            target_mb = stats['total_target_size'] / (1024 * 1024)
            print(f"Original size: {source_mb:.1f} MB")
            print(f"Converted size: {target_mb:.1f} MB")
            print(f"Compression ratio: {stats['compression_ratio']:.1f}%")
        
        # Show failed conversions
        if stats['failed'] > 0:
            print("\nFailed conversions:")
            for result in stats['results']:
                if not result.success:
                    print(f"  {result.source_path}: {result.error_message}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert audio files between different formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --format mp3 *.wav                    # Convert all WAV files to MP3
  %(prog)s --format flac --quality lossless ~/Music  # Convert music folder to lossless FLAC
  %(prog)s --format ogg --output ./converted music.mp3 audio.wav  # Convert specific files
  %(prog)s --format mp3 --quality low --workers 8 ./audio_files/  # Fast batch conversion
        """
    )
    
    parser.add_argument('files', nargs='+', 
                       help='Audio files, directories, or glob patterns to convert')
    parser.add_argument('--format', '-f', required=True,
                       choices=['mp3', 'wav', 'ogg', 'flac'],
                       help='Target audio format')
    parser.add_argument('--quality', '-q', 
                       choices=['low', 'medium', 'high', 'lossless'],
                       default='medium',
                       help='Output quality (default: medium)')
    parser.add_argument('--output', '-o',
                       help='Output directory (default: same as source)')
    parser.add_argument('--overwrite', '-y', action='store_true',
                       help='Overwrite existing files')
    parser.add_argument('--workers', '-w', type=int, default=4,
                       help='Number of parallel conversion threads (default: 4)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize converter
        converter = BatchAudioConverter(
            target_format=args.format,
            quality=args.quality,
            output_dir=args.output,
            overwrite=args.overwrite,
            max_workers=args.workers
        )
        
        # Perform batch conversion
        stats = converter.convert_batch(args.files)
        
        # Print summary
        converter.print_summary(stats)
        
        # Exit with appropriate code
        sys.exit(0 if stats['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\nConversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
