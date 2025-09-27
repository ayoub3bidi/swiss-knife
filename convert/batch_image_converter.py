import sys
import argparse
import glob
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass
from enum import Enum

from PIL import Image, ImageOps 
from PIL.ExifTags import ORIENTATION
import pillow_heif
from tqdm import tqdm


class ResizeMode(Enum):
    EXACT = "exact"          # Exact dimensions (may distort)
    FIT = "fit"             # Fit within dimensions (preserve aspect ratio)
    FILL = "fill"           # Fill dimensions (crop if needed)
    PERCENTAGE = "percent"   # Resize by percentage


@dataclass
class ConversionResult:
    source_path: str
    target_path: str
    success: bool
    error_message: Optional[str] = None
    source_size: Optional[Tuple[int, int]] = None
    target_size: Optional[Tuple[int, int]] = None
    source_file_size: Optional[int] = None
    target_file_size: Optional[int] = None


class BatchImageConverter:
    SUPPORTED_INPUT_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', 
        '.webp', '.gif', '.ico', '.heic', '.heif'
    }
    
    SUPPORTED_OUTPUT_FORMATS = {
        'jpeg': {'extension': '.jpg', 'mode': 'RGB'},
        'png': {'extension': '.png', 'mode': 'RGBA'},
        'webp': {'extension': '.webp', 'mode': 'RGB'},
        'bmp': {'extension': '.bmp', 'mode': 'RGB'},
        'tiff': {'extension': '.tiff', 'mode': 'RGB'},
    }
    
    QUALITY_PRESETS = {
        'low': 60,
        'medium': 80,
        'high': 95,
        'maximum': 100
    }
    
    def __init__(self, target_format: str = None, quality: Union[str, int] = 'high',
                 resize_dimensions: Optional[Tuple[int, int]] = None,
                 resize_mode: ResizeMode = ResizeMode.FIT,
                 resize_percentage: Optional[float] = None,
                 output_dir: Optional[str] = None, overwrite: bool = False,
                 preserve_metadata: bool = True, max_workers: int = 4):
        """
        Args:
            target_format: Output format (jpeg, png, webp, bmp, tiff)
            quality: Quality preset (low, medium, high, maximum) or integer 1-100
            resize_dimensions: Target dimensions (width, height)
            resize_mode: How to handle resizing (exact, fit, fill, percent)
            resize_percentage: Resize percentage (0-100) for percentage mode
            output_dir: Output directory (None = same as source)
            overwrite: Whether to overwrite existing files
            preserve_metadata: Whether to preserve EXIF metadata
            max_workers: Number of parallel conversion threads
        """
        pillow_heif.register_heif_opener()
        
        if target_format and target_format.lower() not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"Unsupported output format: {target_format}")
        
        if isinstance(quality, str) and quality not in self.QUALITY_PRESETS:
            raise ValueError(f"Invalid quality preset: {quality}")
        elif isinstance(quality, int) and not (1 <= quality <= 100):
            raise ValueError(f"Quality must be between 1-100, got: {quality}")
        
        if resize_mode == ResizeMode.PERCENTAGE and resize_percentage is None:
            raise ValueError("resize_percentage required when using percentage mode")
        
        self.target_format = target_format.lower() if target_format else None
        self.quality = self.QUALITY_PRESETS[quality] if isinstance(quality, str) else quality
        self.resize_dimensions = resize_dimensions
        self.resize_mode = resize_mode
        self.resize_percentage = resize_percentage
        self.output_dir = Path(output_dir) if output_dir else None
        self.overwrite = overwrite
        self.preserve_metadata = preserve_metadata
        self.max_workers = max_workers

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_output_path(self, source_path: Path) -> Path:
        if self.target_format:
            target_ext = self.SUPPORTED_OUTPUT_FORMATS[self.target_format]['extension']
        else:
            target_ext = source_path.suffix.lower()
            if target_ext not in {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}:
                target_ext = '.jpg'

        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return self.output_dir / f"{source_path.stem}{target_ext}"
        else:
            return source_path.parent / f"{source_path.stem}{target_ext}"
    
    def _fix_orientation(self, image: Image.Image) -> Image.Image:
        try:
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(ORIENTATION)
                if orientation:
                    if orientation == 2:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 4:
                        image = image.rotate(180, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 5:
                        image = image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 6:
                        image = image.rotate(-90, expand=True)
                    elif orientation == 7:
                        image = image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            pass
        return image
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        if not self.resize_dimensions and not self.resize_percentage:
            return image
        
        original_size = image.size
        
        if self.resize_mode == ResizeMode.PERCENTAGE:
            if self.resize_percentage:
                factor = self.resize_percentage / 100
                new_size = (int(original_size[0] * factor), int(original_size[1] * factor))
                return image.resize(new_size, Image.Resampling.LANCZOS)
        
        elif self.resize_dimensions:
            target_width, target_height = self.resize_dimensions
            
            if self.resize_mode == ResizeMode.EXACT:
                return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            elif self.resize_mode == ResizeMode.FIT:
                image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                return image
            
            elif self.resize_mode == ResizeMode.FILL:
                return ImageOps.fit(image, (target_width, target_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _convert_single_image(self, source_path: Path) -> ConversionResult:
        try:
            target_path = self._get_output_path(source_path)

            if target_path.exists() and not self.overwrite:
                return ConversionResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message="Target file exists (use --overwrite to replace)"
                )

            source_file_size = source_path.stat().st_size

            try:
                with Image.open(source_path) as image:
                    original_size = image.size
                    image = self._fix_orientation(image)
                    image = self._resize_image(image)

                    if self.target_format:
                        target_mode = self.SUPPORTED_OUTPUT_FORMATS[self.target_format]['mode']
                        if image.mode != target_mode:
                            if target_mode == 'RGB' and image.mode in ('RGBA', 'P'):
                                background = Image.new('RGB', image.size, (255, 255, 255))
                                if image.mode == 'P':
                                    image = image.convert('RGBA')
                                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                                image = background
                            else:
                                image = image.convert(target_mode)

                    save_kwargs = {}
                    if self.target_format == 'jpeg' or (not self.target_format and target_path.suffix.lower() in ['.jpg', '.jpeg']):
                        save_kwargs['quality'] = self.quality
                        save_kwargs['optimize'] = True
                    elif self.target_format == 'webp':
                        save_kwargs['quality'] = self.quality
                        save_kwargs['optimize'] = True
                    elif self.target_format == 'png':
                        save_kwargs['optimize'] = True

                    if self.preserve_metadata and hasattr(image, '_getexif'):
                        exif = image.info.get('exif')
                        if exif:
                            save_kwargs['exif'] = exif

                    image.save(target_path, **save_kwargs)
            
            except Exception as e:
                return ConversionResult(
                    source_path=str(source_path),
                    target_path=str(target_path),
                    success=False,
                    error_message=f"Image processing error: {e}"
                )

            target_file_size = target_path.stat().st_size
            with Image.open(target_path) as final_image:
                target_size = final_image.size
            
            return ConversionResult(
                source_path=str(source_path),
                target_path=str(target_path),
                success=True,
                source_size=original_size,
                target_size=target_size,
                source_file_size=source_file_size,
                target_file_size=target_file_size
            )
            
        except Exception as e:
            return ConversionResult(
                source_path=str(source_path),
                target_path=str(target_path) if 'target_path' in locals() else '',
                success=False,
                error_message=str(e)
            )
    
    def _find_image_files(self, paths: List[str]) -> List[Path]:
        files = []
        
        for path_pattern in paths:
            if '*' in path_pattern or '?' in path_pattern:
                matched_files = glob.glob(path_pattern)
                for file_path in matched_files:
                    p = Path(file_path)
                    if p.is_file() and p.suffix.lower() in self.SUPPORTED_INPUT_FORMATS:
                        files.append(p)
            else:
                path = Path(path_pattern)
                if path.is_file():
                    if path.suffix.lower() in self.SUPPORTED_INPUT_FORMATS:
                        files.append(path)
                elif path.is_dir():
                    for ext in self.SUPPORTED_INPUT_FORMATS:
                        files.extend(path.rglob(f'*{ext}'))
                        files.extend(path.rglob(f'*{ext.upper()}'))
        
        return sorted(set(files))
    
    def convert_batch(self, paths: List[str]) -> Dict[str, any]:
        """
        Args: paths: List of file paths, directories, or glob patterns
        Returns: Dictionary with conversion statistics and results
        """
        image_files = self._find_image_files(paths)
        
        if not image_files:
            self.logger.warning("No image files found for processing")
            return {
                'total_files': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        operation = "Converting" if self.target_format else "Processing"
        if self.resize_dimensions or self.resize_percentage:
            operation += "/Resizing"
        
        self.logger.info(f"Found {len(image_files)} files to process")

        results = []
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._convert_single_image, file_path): file_path 
                for file_path in image_files
            }

            with tqdm(total=len(image_files), desc=f"{operation} images") as pbar:
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        successful += 1
                        if result.source_file_size and result.target_file_size:
                            ratio = (result.target_file_size / result.source_file_size) * 100
                            pbar.set_postfix({
                                'Success': f"{successful}/{len(image_files)}",
                                'Size': f"{ratio:.1f}%"
                            })
                    else:
                        failed += 1
                        self.logger.error(f"Failed to process {result.source_path}: {result.error_message}")
                        pbar.set_postfix({
                            'Success': f"{successful}/{len(image_files)}",
                            'Failed': failed
                        })
                    
                    pbar.update(1)

        total_source_size = sum(r.source_file_size for r in results if r.source_file_size)
        total_target_size = sum(r.target_file_size for r in results if r.target_file_size)
        
        stats = {
            'total_files': len(image_files),
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
        print("IMAGE PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"Total files processed: {stats['total_files']}")
        print(f"Successfully processed: {stats['successful']}")
        print(f"Failed operations: {stats['failed']}")
        
        if stats['total_source_size'] > 0:
            source_mb = stats['total_source_size'] / (1024 * 1024)
            target_mb = stats['total_target_size'] / (1024 * 1024)
            print(f"Original size: {source_mb:.1f} MB")
            print(f"Processed size: {target_mb:.1f} MB")
            print(f"Size ratio: {stats['compression_ratio']:.1f}%")
        
        # Show failed operations
        if stats['failed'] > 0:
            print("\nFailed operations:")
            for result in stats['results']:
                if not result.success:
                    print(f"  {result.source_path}: {result.error_message}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert and resize images between different formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --format jpeg --quality 80 *.png                    # Convert PNG to JPEG
  %(prog)s --resize 800x600 --mode fit ~/Photos/               # Resize images to fit 800x600
  %(prog)s --format webp --resize 1920x1080 --mode fill *.jpg  # Convert and resize with cropping
  %(prog)s --percentage 50 --output ./thumbnails/ images/      # Create 50%% thumbnails
  %(prog)s --format png --quality maximum --preserve-metadata *.heic  # Convert HEIC to PNG
        """
    )
    
    parser.add_argument('files', nargs='+', 
                       help='Image files, directories, or glob patterns to process')
    parser.add_argument('--format', '-f', 
                       choices=['jpeg', 'png', 'webp', 'bmp', 'tiff'],
                       help='Target image format (optional - keeps original if not specified)')
    parser.add_argument('--quality', '-q', 
                       default='high',
                       help='Output quality: low, medium, high, maximum, or integer 1-100 (default: high)')
    parser.add_argument('--resize', '-r', 
                       help='Resize dimensions as WIDTHxHEIGHT (e.g., 800x600)')
    parser.add_argument('--mode', '-m', 
                       choices=['exact', 'fit', 'fill', 'percent'],
                       default='fit',
                       help='Resize mode (default: fit)')
    parser.add_argument('--percentage', '-p', type=float,
                       help='Resize percentage (use with --mode percent)')
    parser.add_argument('--output', '-o',
                       help='Output directory (default: same as source)')
    parser.add_argument('--overwrite', '-y', action='store_true',
                       help='Overwrite existing files')
    parser.add_argument('--preserve-metadata', action='store_true', default=True,
                       help='Preserve EXIF metadata (default: enabled)')
    parser.add_argument('--no-preserve-metadata', dest='preserve_metadata', action='store_false',
                       help='Do not preserve EXIF metadata')
    parser.add_argument('--workers', '-w', type=int, default=4,
                       help='Number of parallel processing threads (default: 4)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        quality = int(args.quality)
    except ValueError:
        quality = args.quality

    resize_dimensions = None
    if args.resize:
        try:
            width, height = map(int, args.resize.split('x'))
            resize_dimensions = (width, height)
        except ValueError:
            print(f"Error: Invalid resize format '{args.resize}'. Use WIDTHxHEIGHT (e.g., 800x600)")
            sys.exit(1)

    resize_mode = ResizeMode(args.mode)
    
    try:
        converter = BatchImageConverter(
            target_format=args.format,
            quality=quality,
            resize_dimensions=resize_dimensions,
            resize_mode=resize_mode,
            resize_percentage=args.percentage,
            output_dir=args.output,
            overwrite=args.overwrite,
            preserve_metadata=args.preserve_metadata,
            max_workers=args.workers
        )

        stats = converter.convert_batch(args.files)
        converter.print_summary(stats)

        sys.exit(0 if stats['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
