#!/usr/bin/env python3

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import (
        SquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer,
        VerticalBarsDrawer, HorizontalBarsDrawer, GappedSquareModuleDrawer
    )
    from qrcode.image.styles.colormasks import SolidFillColorMask
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Error: qrcode not installed. Run: pip install 'qrcode[pil]'")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class QRGenerator:
    
    STYLES = {
        'square': SquareModuleDrawer,
        'circle': CircleModuleDrawer,
        'rounded': RoundedModuleDrawer,
        'vertical': VerticalBarsDrawer,
        'horizontal': HorizontalBarsDrawer,
        'gapped': GappedSquareModuleDrawer
    }
    
    def __init__(self,
                 version: Optional[int] = None,
                 error_correction: str = 'M',
                 box_size: int = 10,
                 border: int = 4,
                 fill_color: str = 'black',
                 back_color: str = 'white',
                 style: str = 'square'):
        """
        Args:
            version: QR code version (1-40, None=auto)
            error_correction: L, M, Q, H (Low to High)
            box_size: Size of each box in pixels
            border: Border size in boxes
            fill_color: Foreground color
            back_color: Background color
            style: Module style (square, circle, rounded, etc.)
        """
        self.version = version
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color
        self.style = style
        
        # Map error correction
        error_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        self.error_correction = error_map.get(error_correction.upper(), 
                                              qrcode.constants.ERROR_CORRECT_M)
        
        self.stats = {
            'generated': 0,
            'failed': 0
        }
    
    def _create_qr(self) -> qrcode.QRCode:
        """Create QR code instance."""
        return qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border
        )
    
    def _parse_color(self, color: str) -> tuple:
        """Parse color string to RGB tuple."""
        if color.startswith('#'):
            color = color.lstrip('#')
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        color_map = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128)
        }
        return color_map.get(color.lower(), (0, 0, 0))
    
    def generate(self, data: str, output_path: Optional[Path] = None,
                add_label: Optional[str] = None) -> Optional[Image.Image]:
        """Generate QR code from data."""
        try:
            qr = self._create_qr()
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image with style
            if self.style != 'square':
                module_drawer = self.STYLES.get(self.style, SquareModuleDrawer)()
                
                fill_rgb = self._parse_color(self.fill_color)
                back_rgb = self._parse_color(self.back_color)
                color_mask = SolidFillColorMask(back_color=back_rgb, front_color=fill_rgb)
                
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask
                )
            else:
                img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
            
            # Add label if requested
            if add_label:
                img = self._add_label(img, add_label)
            
            # Save if path provided
            if output_path:
                img.save(output_path)
                self.stats['generated'] += 1
            
            return img
        
        except Exception as e:
            print(f"Error generating QR code: {e}")
            self.stats['failed'] += 1
            return None
    
    def _add_label(self, img: Image.Image, label: str, 
                   padding: int = 20, font_size: int = 24) -> Image.Image:
        """Add text label below QR code."""
        if not HAS_PIL:
            return img
        
        # Create new image with space for label
        label_height = font_size + padding * 2
        new_height = img.size[1] + label_height
        new_img = Image.new('RGB', (img.size[0], new_height), self.back_color)
        
        # Paste original QR code
        new_img.paste(img, (0, 0))
        
        # Draw label
        draw = ImageDraw.Draw(new_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (img.size[0] - text_width) // 2
        text_y = img.size[1] + padding
        
        draw.text((text_x, text_y), label, fill=self.fill_color, font=font)
        
        return new_img
    
    def generate_url(self, url: str, output_path: Path, label: Optional[str] = None):
        """Generate QR code for URL."""
        return self.generate(url, output_path, add_label=label)
    
    def generate_text(self, text: str, output_path: Path, label: Optional[str] = None):
        """Generate QR code for plain text."""
        return self.generate(text, output_path, add_label=label)
    
    def generate_wifi(self, ssid: str, password: str, security: str = 'WPA',
                     hidden: bool = False, output_path: Optional[Path] = None,
                     label: Optional[str] = None):
        """Generate WiFi QR code."""
        # WiFi format: WIFI:T:WPA;S:mynetwork;P:mypass;H:false;;
        hidden_str = 'true' if hidden else 'false'
        wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_str};;"
        return self.generate(wifi_string, output_path, add_label=label)
    
    def generate_vcard(self, name: str, phone: Optional[str] = None,
                      email: Optional[str] = None, organization: Optional[str] = None,
                      url: Optional[str] = None, output_path: Optional[Path] = None,
                      label: Optional[str] = None):
        """Generate vCard (contact) QR code."""
        vcard = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]
        
        if phone:
            vcard.append(f"TEL:{phone}")
        if email:
            vcard.append(f"EMAIL:{email}")
        if organization:
            vcard.append(f"ORG:{organization}")
        if url:
            vcard.append(f"URL:{url}")
        
        vcard.append("END:VCARD")
        vcard_string = "\n".join(vcard)
        
        return self.generate(vcard_string, output_path, add_label=label)
    
    def generate_email(self, email: str, subject: Optional[str] = None,
                      body: Optional[str] = None, output_path: Optional[Path] = None,
                      label: Optional[str] = None):
        """Generate email QR code."""
        mailto = f"mailto:{email}"
        
        params = []
        if subject:
            params.append(f"subject={subject}")
        if body:
            params.append(f"body={body}")
        
        if params:
            mailto += "?" + "&".join(params)
        
        return self.generate(mailto, output_path, add_label=label)
    
    def generate_sms(self, phone: str, message: Optional[str] = None,
                    output_path: Optional[Path] = None, label: Optional[str] = None):
        """Generate SMS QR code."""
        sms = f"SMSTO:{phone}"
        if message:
            sms += f":{message}"
        return self.generate(sms, output_path, add_label=label)
    
    def generate_phone(self, phone: str, output_path: Optional[Path] = None,
                      label: Optional[str] = None):
        """Generate phone call QR code."""
        tel = f"tel:{phone}"
        return self.generate(tel, output_path, add_label=label)
    
    def generate_geo(self, latitude: float, longitude: float,
                    output_path: Optional[Path] = None, label: Optional[str] = None):
        """Generate geolocation QR code."""
        geo = f"geo:{latitude},{longitude}"
        return self.generate(geo, output_path, add_label=label)
    
    def generate_batch_from_file(self, filepath: Path, output_dir: Path,
                                 name_template: str = "qr_{:03d}.png"):
        """Generate QR codes from file (one per line)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not lines:
                print(f"No data found in {filepath}")
                return
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Generating {len(lines)} QR code(s)...")
            iterator = tqdm(enumerate(lines, 1), total=len(lines), 
                          desc="Generating", unit="QR") if HAS_TQDM else enumerate(lines, 1)
            
            for i, line in iterator:
                output_path = output_dir / name_template.format(i)
                self.generate(line, output_path)
            
            print(f"\n✓ Generated {self.stats['generated']} QR code(s) in {output_dir}")
            
        except Exception as e:
            print(f"Error reading file: {e}")
    
    def generate_batch_from_json(self, filepath: Path, output_dir: Path):
        """Generate QR codes from JSON file with metadata."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Generating {len(data)} QR code(s)...")
            iterator = tqdm(data, desc="Generating", unit="QR") if HAS_TQDM else data
            
            for item in iterator:
                qr_type = item.get('type', 'text')
                output_name = item.get('output', f"qr_{qr_type}_{self.stats['generated']+1}.png")
                output_path = output_dir / output_name
                label = item.get('label')
                
                if qr_type == 'url':
                    self.generate_url(item['data'], output_path, label)
                elif qr_type == 'wifi':
                    self.generate_wifi(
                        item['ssid'], item['password'],
                        item.get('security', 'WPA'),
                        item.get('hidden', False),
                        output_path, label
                    )
                elif qr_type == 'vcard':
                    self.generate_vcard(
                        item['name'],
                        item.get('phone'),
                        item.get('email'),
                        item.get('organization'),
                        item.get('url'),
                        output_path, label
                    )
                elif qr_type == 'email':
                    self.generate_email(
                        item['email'],
                        item.get('subject'),
                        item.get('body'),
                        output_path, label
                    )
                elif qr_type == 'text':
                    self.generate_text(item['data'], output_path, label)
            
            print(f"\n✓ Generated {self.stats['generated']} QR code(s) in {output_dir}")
            
        except Exception as e:
            print(f"Error processing JSON: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate QR codes for URLs, WiFi, contacts, and more",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # URL QR code
  python qr_generator.py --url https://example.com -o qr.png
  
  # WiFi QR code
  python qr_generator.py --wifi --ssid MyNetwork --password mypass123 -o wifi_qr.png
  
  # Contact card (vCard)
  python qr_generator.py --vcard --name "John Doe" --phone "+1234567890" --email john@example.com -o contact.png
  
  # Plain text with custom styling
  python qr_generator.py --text "Hello World" -o text.png --style rounded --fill-color blue
  
  # Batch generation from file
  python qr_generator.py --batch urls.txt --output-dir qr_codes/
  
  # Batch from JSON with metadata
  python qr_generator.py --batch-json config.json --output-dir qr_codes/
  
  # Email QR code
  python qr_generator.py --email contact@example.com --subject "Hello" -o email_qr.png
  
  # Phone call QR code
  python qr_generator.py --phone "+1234567890" -o phone_qr.png
  
  # SMS QR code
  python qr_generator.py --sms "+1234567890" --message "Hello" -o sms_qr.png
  
  # Geolocation QR code
  python qr_generator.py --geo 40.7128 -74.0060 -o location_qr.png
"""
    )
    
    # Mode selection
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--url', type=str, help='Generate URL QR code')
    mode.add_argument('--text', type=str, help='Generate text QR code')
    mode.add_argument('--wifi', action='store_true', help='Generate WiFi QR code')
    mode.add_argument('--vcard', action='store_true', help='Generate vCard (contact) QR code')
    mode.add_argument('--email', type=str, help='Generate email QR code')
    mode.add_argument('--sms', type=str, help='Generate SMS QR code (phone number)')
    mode.add_argument('--phone', type=str, help='Generate phone call QR code')
    mode.add_argument('--geo', nargs=2, type=float, metavar=('LAT', 'LON'),
                     help='Generate geolocation QR code')
    mode.add_argument('--batch', type=Path, help='Batch generate from text file')
    mode.add_argument('--batch-json', type=Path, help='Batch generate from JSON file')
    
    # WiFi options
    parser.add_argument('--ssid', type=str, help='WiFi SSID')
    parser.add_argument('--password', type=str, help='WiFi password')
    parser.add_argument('--security', default='WPA', choices=['WPA', 'WEP', 'nopass'],
                       help='WiFi security type')
    parser.add_argument('--hidden', action='store_true', help='Hidden WiFi network')
    
    # vCard options
    parser.add_argument('--name', type=str, help='Contact name')
    parser.add_argument('--vcard-phone', dest='vcard_phone', type=str, help='Contact phone')
    parser.add_argument('--vcard-email', dest='vcard_email', type=str, help='Contact email')
    parser.add_argument('--organization', type=str, help='Contact organization')
    parser.add_argument('--vcard-url', dest='vcard_url', type=str, help='Contact URL')
    
    # Email options
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--body', type=str, help='Email body')
    
    # SMS options
    parser.add_argument('--message', type=str, help='SMS message')
    
    # Output options
    parser.add_argument('-o', '--output', type=Path, help='Output file path')
    parser.add_argument('--output-dir', type=Path, help='Output directory for batch generation')
    parser.add_argument('--label', type=str, help='Add text label below QR code')
    
    # QR code customization
    parser.add_argument('--version', type=int, choices=range(1, 41),
                       help='QR code version (1-40, default: auto)')
    parser.add_argument('--error-correction', default='M', choices=['L', 'M', 'Q', 'H'],
                       help='Error correction level (default: M)')
    parser.add_argument('--box-size', type=int, default=10,
                       help='Box size in pixels (default: 10)')
    parser.add_argument('--border', type=int, default=4,
                       help='Border size in boxes (default: 4)')
    parser.add_argument('--fill-color', default='black',
                       help='Foreground color (name or #RRGGBB)')
    parser.add_argument('--back-color', default='white',
                       help='Background color (name or #RRGGBB)')
    parser.add_argument('--style', default='square',
                       choices=['square', 'circle', 'rounded', 'vertical', 'horizontal', 'gapped'],
                       help='QR code style (default: square)')
    
    args = parser.parse_args()
    
    # Validation
    if not HAS_QRCODE:
        print("Error: qrcode library required. Install: pip install 'qrcode[pil]'")
        sys.exit(1)
    
    if args.wifi and (not args.ssid or not args.password):
        parser.error("--wifi requires --ssid and --password")
    
    if args.vcard and not args.name:
        parser.error("--vcard requires --name")
    
    if not args.batch and not args.batch_json and not args.output:
        parser.error("--output is required for single QR code generation")
    
    if (args.batch or args.batch_json) and not args.output_dir:
        parser.error("--output-dir is required for batch generation")
    
    try:
        # Initialize generator
        generator = QRGenerator(
            version=args.version,
            error_correction=args.error_correction,
            box_size=args.box_size,
            border=args.border,
            fill_color=args.fill_color,
            back_color=args.back_color,
            style=args.style
        )
        
        # Generate based on mode
        if args.url:
            generator.generate_url(args.url, args.output, args.label)
            print(f"✓ URL QR code saved to {args.output}")
        
        elif args.text:
            generator.generate_text(args.text, args.output, args.label)
            print(f"✓ Text QR code saved to {args.output}")
        
        elif args.wifi:
            generator.generate_wifi(
                args.ssid, args.password, args.security,
                args.hidden, args.output, args.label
            )
            print(f"✓ WiFi QR code saved to {args.output}")
        
        elif args.vcard:
            generator.generate_vcard(
                args.name, args.vcard_phone, args.vcard_email,
                args.organization, args.vcard_url, args.output, args.label
            )
            print(f"✓ vCard QR code saved to {args.output}")
        
        elif args.email:
            generator.generate_email(args.email, args.subject, args.body, args.output, args.label)
            print(f"✓ Email QR code saved to {args.output}")
        
        elif args.sms:
            generator.generate_sms(args.sms, args.message, args.output, args.label)
            print(f"✓ SMS QR code saved to {args.output}")
        
        elif args.phone:
            generator.generate_phone(args.phone, args.output, args.label)
            print(f"✓ Phone QR code saved to {args.output}")
        
        elif args.geo:
            generator.generate_geo(args.geo[0], args.geo[1], args.output, args.label)
            print(f"✓ Geolocation QR code saved to {args.output}")
        
        elif args.batch:
            generator.generate_batch_from_file(args.batch, args.output_dir)
        
        elif args.batch_json:
            generator.generate_batch_from_json(args.batch_json, args.output_dir)
        
        sys.exit(0 if generator.stats['failed'] == 0 else 1)
    
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
