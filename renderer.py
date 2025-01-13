from typing import Dict, List, Optional
from pathlib import Path
import base64
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import textwrap  # Add this import at the top

class CLIStyleRenderer:
    def __init__(
        self,
        font_path: Optional[str] = None,
        emoji_font_path: Optional[str] = None,
        output_dir: str = "outputs",
        style_config: Optional[Dict] = None,
        cjk: bool = False
    ):
        """Initialize with custom styles for different line prefixes."""
        self.default_style_config = {
            ">>": {  # Command style
                "color": (0, 255, 255),  # Cyan
                "glow": True,
                "prefix": ">>",
                "indent": 0
            },
            "$": {   # Output style
                "color": (0, 255, 0),    # Green
                "glow": True,
                "prefix": "$",
                "indent": 20
            },
            "#": {   # Comment style
                "color": (128, 128, 128), # Gray
                "glow": False,
                "prefix": "#",
                "indent": 10
            },
            "!": {   # Error/Warning style
                "color": (255, 0, 0),     # Red
                "glow": True,
                "prefix": "!",
                "indent": 0
            },
            "@": {   # Info style
                "color": (255, 255, 0),   # Yellow
                "glow": True,
                "prefix": "@",
                "indent": 10
            },
            "img": { # Image style
                "color": (255, 128, 255), # Pink
                "glow": True,
                "prefix": "",
                "indent": 20,
                "max_height": 300
            }
        }
        
        self.style_config = {**self.default_style_config, **(style_config or {})}
        self.emoji_font_path = emoji_font_path or "fonts/NotoColorEmoji.ttf"
        # Use Noto Sans CJK which supports CJK characters
        if cjk:
            self.font_path = font_path or "fonts/NotoSansCJK-Regular.ttc"
        else:
            self.font_path = font_path or "fonts/DejaVuSans.ttf"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.font_size = 80
        self.emoji_font_size = 109
        # Initialize fonts with fallback
        try:
            self.font = ImageFont.truetype(self.font_path, size=self.font_size, layout_engine=ImageFont.Layout.BASIC)
        except Exception as e:
            print(f"Failed to load CJK font: {e}")
            # Fallback to DejaVuSans if CJK font is not available
            self.font = ImageFont.truetype("fonts/DejaVuSans.ttf", size=self.font_size, layout_engine=ImageFont.Layout.BASIC)
        
        self.emoji_font = ImageFont.truetype(self.emoji_font_path, size=self.emoji_font_size, layout_engine=ImageFont.Layout.BASIC)

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

    def _is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji."""
        return any(u"\U0001F300" <= c <= u"\U0001FAF6" for c in char)

    def _get_text_width(self, text: str) -> int:
        """Get the width of text, accounting for CJK characters, regular text and emojis."""
        total_width = 0
        for char in text:
            if self._is_emoji(char):
                bbox = self.emoji_font.getbbox(char)
            else:
                bbox = self.font.getbbox(char)
            if bbox:
                total_width += bbox[2] - bbox[0]
        return total_width

    def generate_cli_image(
        self,
        lines: List[str],
        width: int = 1920,
        padding: int = 80,
        show_chrome: bool = True
    ) -> str:
        """Generate CLI image from text lines with different styles."""
        # Helper function to calculate character limit
        def get_char_limit(text: str, max_width: int) -> int:
            left = 1
            right = len(text)
            while left <= right:
                mid = (left + right) // 2
                test_text = text[:mid]
                text_width = self._get_text_width(test_text)
                if text_width <= max_width:
                    left = mid + 1
                else:
                    right = mid - 1
            return right

        # First calculate all wrapped lines to get accurate height
        line_height = int(self.font_size * 1.5)
        total_height = padding * 2
        if show_chrome:
            total_height += 30  # Header height

        all_wrapped_lines = []  # Store all wrapped lines for later use
        for line in lines:
            line = line.strip()
            if not line:
                all_wrapped_lines.append([])
                total_height += line_height
                continue

            if line.startswith(("img_left:", "img_center:")):
                image_path = line.split(":", 1)[1].strip()
                img_obj = self._process_image(
                    image_path, 
                    self.style_config["img"]["max_height"]
                )
                if img_obj:
                    total_height += img_obj.height + 10
                all_wrapped_lines.append(["img:" + line])  # Mark as image line
            else:
                # Calculate available width for this line
                style = next((s for p, s in self.style_config.items() if line.startswith(p)), 
                           self.style_config["$"])
                available_width = width - (2 * padding) - style["indent"]
                
                # Calculate wrapped lines based on pixel width
                wrapped_lines = []
                remaining = line
                while remaining:
                    char_limit = get_char_limit(remaining, available_width)
                    if char_limit == 0:  # Fallback if calculation fails
                        char_limit = len(remaining)
                    wrapped_lines.append(remaining[:char_limit])
                    remaining = remaining[char_limit:].lstrip()
                
                all_wrapped_lines.append(wrapped_lines)
                total_height += line_height * len(wrapped_lines)

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

        # Draw lines using pre-calculated wrapping
        for i, wrapped_lines in enumerate(all_wrapped_lines):
            if not wrapped_lines:
                current_y += line_height
                continue

            original_line = lines[i].strip()
            if wrapped_lines[0].startswith("img:"):
                # Handle image
                image_line = wrapped_lines[0][4:]  # Remove "img:" prefix
                align = "center" if image_line.startswith("img_center:") else "left"
                image_path = image_line.split(":", 1)[1].strip()
                img_obj = self._process_image(
                    image_path, 
                    self.style_config["img"]["max_height"],
                    align
                )
                if img_obj:
                    if align == "center":
                        img_x = (width - img_obj.width) // 2
                    else:
                        img_x = padding + self.style_config["img"]["indent"]
                    img.paste(img_obj, (img_x, current_y))
                    current_y += img_obj.height + 10
            else:
                # Handle text
                style = next((s for p, s in self.style_config.items() if original_line.startswith(p)), 
                           self.style_config["$"])
                x = padding + style["indent"]
                for wrapped_line in wrapped_lines:
                    self.draw_text_with_emojis(
                        draw,
                        x,
                        current_y,
                        wrapped_line,
                        style["color"]
                    )
                    current_y += line_height

        # Add border
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
        header_height = 60
        draw.rectangle([(0, 0), (width, header_height)], fill=(30, 30, 30))
        
        # Larger terminal buttons
        button_colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
        for i, color in enumerate(button_colors):
            draw.ellipse([(20 + i*50, 15), (50 + i*50, 45)], fill=color)
            
        return header_height
    
    def save_image_by_timestamp(self, img_base64: str, filename: str) -> None:
        """Save image with a timestamp in the filename."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename}_{timestamp}.png"
        with open(os.path.join(self.output_dir, filename), "wb") as f:
            f.write(base64.b64decode(img_base64))

    def draw_text_with_emojis(self, draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color: tuple):
        current_x = x
        for char in text:
            if self._is_emoji(char):
                bbox = self.emoji_font.getbbox(char)
                if bbox:
                    # Adjusted vertical offset for better alignment with larger text
                    draw.text((current_x, y - 15), char, font=self.emoji_font, embedded_color=True)
                    current_x += bbox[2] - bbox[0]
            else:
                bbox = self.font.getbbox(char)
                if bbox:
                    draw.text((current_x, y), char, font=self.font, fill=color)
                    current_x += bbox[2] - bbox[0]