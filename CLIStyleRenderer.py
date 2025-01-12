from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import base64
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import json

class CLIStyleRenderer:
    def __init__(
        self,
        font_path: Optional[str] = None,
        output_dir: str = "outputs",
        style_config: Optional[Dict] = None
    ):
        """Initialize with custom styles for different line prefixes."""
        self.default_style_config = {
            ">>": {  # Command style
                "color": [0, 255, 255],  # Cyan
                "glow": True,
                "prefix": ">>",
                "indent": 0
            },
            "$": {   # Output style
                "color": [0, 255, 0],    # Green
                "glow": True,
                "prefix": "$",
                "indent": 20
            },
            "#": {   # Comment style
                "color": [128, 128, 128], # Gray
                "glow": False,
                "prefix": "#",
                "indent": 10
            },
            "!": {   # Error/Warning style
                "color": [255, 0, 0],     # Red
                "glow": True,
                "prefix": "!",
                "indent": 0
            },
            "@": {   # Info style
                "color": [255, 255, 0],   # Yellow
                "glow": True,
                "prefix": "@",
                "indent": 10
            },
            "img": { # Image style
                "color": [255, 128, 255], # Pink
                "glow": True,
                "prefix": "",
                "indent": 20,
                "max_height": 300
            }
        }
        
        self.style_config = {**self.default_style_config, **(style_config or {})}
        self.font_path = font_path or "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _process_image(self, image_path: str, max_height: int, align: str = "left") -> Optional[Image.Image]:
        """Process image from URL or local path."""
        try:
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_path)

            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize maintaining aspect ratio
            if img.height > max_height:
                ratio = max_height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)

            return img
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def generate_cli_image(
        self,
        lines: List[str],
        width: int = 1200,
        padding: int = 40,
        font_size: int = 24,
        show_chrome: bool = True
    ) -> str:
        """Generate CLI image from text lines with different styles."""
        # First pass: calculate total height including images
        line_height = int(font_size * 1.5)
        total_height = padding * 2
        if show_chrome:
            total_height += 30  # Header height

        # Pre-calculate height by processing images first
        for line in lines:
            line = line.strip()
            if line.startswith(("img_left:", "img_center:")):
                image_path = line.split(":", 1)[1].strip()
                img_obj = self._process_image(
                    image_path, 
                    self.style_config["img"]["max_height"]
                )
                if img_obj:
                    total_height += img_obj.height + 10  # Image height + padding
            else:
                total_height += line_height  # Regular line height

        # Create image with calculated height
        img = Image.new("RGB", (width, total_height), (0, 0, 20))
        draw = ImageDraw.Draw(img)

        # Add grid pattern
        for x in range(0, width, 20):
            draw.line([(x, 0), (x, total_height)], fill=(20, 20, 40))
        for y in range(0, total_height, 20):
            draw.line([(0, y), (width, y)], fill=(20, 20, 40))

        # Add window chrome first
        current_y = padding
        if show_chrome:
            current_y += self._add_window_chrome(draw, width)

        # Process each line
        for line in lines:
            line = line.strip()
            if not line:
                current_y += line_height
                continue

            # Handle image lines with alignment
            if line.startswith(("img_left:", "img_center:")):
                align = "center" if line.startswith("img_center:") else "left"
                image_path = line.split(":", 1)[1].strip()
                img_obj = self._process_image(
                    image_path, 
                    self.style_config["img"]["max_height"],
                    align
                )
                if img_obj:
                    if align == "center":
                        img_x = (width - img_obj.width) // 2
                    else:  # left align
                        img_x = padding + self.style_config["img"]["indent"]
                    
                    img.paste(img_obj, (img_x, current_y))
                    current_y += img_obj.height + 10
                continue

            # Determine line style
            style = None
            for prefix in self.style_config:
                if line.startswith(prefix):
                    style = self.style_config[prefix]
                    break
            
            if not style:
                style = self.style_config["$"]  # Default style

            # Draw line with style
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            x = padding + style["indent"]
            draw.text(
                (x, current_y),
                line,
                font=font,
                fill=style["color"]
            )
            current_y += line_height

        # Add clean border without glow, with adjusted padding for chrome
        border_color = (0, 255, 255)
        top_padding = padding//2 + (30 if show_chrome else 0)
        draw.rounded_rectangle(
            [(padding//2, top_padding), 
             (width-padding//2, total_height-padding//2)],
            radius=20,
            outline=border_color,
            width=2
        )

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode()

    def _add_window_chrome(self, draw: ImageDraw.ImageDraw, width: int) -> int:
        """Add terminal window chrome and return header height."""
        header_height = 30
        draw.rectangle([(0, 0), (width, header_height)], fill=(30, 30, 30))
        
        # Terminal buttons
        button_colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
        for i, color in enumerate(button_colors):
            draw.ellipse([(10 + i*25, 8), (25 + i*25, 23)], fill=color)
            
        return header_height
    
    def save_image_by_timestamp(self, img_base64: str, filename: str) -> None:
        """Save image with a timestamp in the filename."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename}_{timestamp}.png"
        with open(os.path.join(self.output_dir, filename), "wb") as f:
            f.write(base64.b64decode(img_base64))

if __name__ == "__main__":
    # Load custom styles from JSON
    with open('style_config.json', 'r') as f:
        custom_styles = json.load(f)
        
    # Create with custom styles
    generator = CLIStyleRenderer(style_config=custom_styles)

    # Example usage with different line styles
    lines = [
        ">> System Analysis",
        "$ Checking components...",
        "# This is a comment",
        "! Warning: High CPU usage",
        "@ Info: 8GB RAM available",
        "img_left: https://pbs.twimg.com/ext_tw_video_thumb/1858064790821974016/pu/img/MQU4WFGD8vSyb_A2.jpg",
        "img_center: images/bear_ryan.png",
        ">>> Custom style line"
    ]

    # Generate image
    img_base64 = generator.generate_cli_image(
        lines,
        width=1200,
        padding=40,
        font_size=24,
        show_chrome=True
    )

    # Save image
    generator.save_image_by_timestamp(img_base64, "output")
