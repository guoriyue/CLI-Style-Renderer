# CLI Style Renderer

## Overview
CLI Style Renderer is a Python script designed to generate styled images resembling terminal or command-line outputs. The script takes a set of input lines, including text, comments, warnings, and embedded images (both local and remote), and renders them into a visually cohesive image with customizable styles.

## Features
- **Text Rendering**: Supports rendering of text with different prefixes (`>>`, `$`, `#`, `!`, `@`, `>>>`) to represent different styles (e.g., system messages, commands, comments, warnings, info).
- **Image Embedding**: Allows embedding images from local files or remote URLs into specific positions (e.g., left, center, right).
- **Customizable Styles**: Users can modify styles to match their needs, including fonts, colors, and background themes.
- **Lightweight**: Minimal dependencies and easy-to-extend design.

## Example Input
```python
lines = [
    ">> System Analysis",
    "$ Checking components...",
    "# This is a comment",
    "! Warning: High CPU usage",
    "@ Info: 8GB RAM available",
    "img_left: https://pbs.twimg.com/ext_tw_video_thumb/1858064790821974016/pu/img/MQU4WFGD8vSyb_A2.jpg",  # Remote image
    "img_center: images/bear_ryan.png",              # Local image
    ">>> Custom style line"
]
```

## Rendered Output
The script processes the input lines and generates an image with the specified layout and styles. 

## Installation
```bash
git clone https://github.com/yourusername/cli-style-renderer.git
cd cli-style-renderer
pip install -r requirements.txt
```

## Usage
1. Prepare your input lines in a Python list or a file.
2. Run the script with the input file or directly pass the lines to the function.
3. Generated images will be saved in the specified output directory.

### Example Command
```bash
python render_cli_style.py --input input_lines.txt --output output_image.png
```

## Configuration
Styles and settings can be customized by modifying the `config.json` file:
```json
{
    "font": "Arial",
    "font_size": 14,
    "background_color": "#000000",
    "text_color": "#FFFFFF",
    "image_width": 800,
    "image_height": 600
}
```

## License
This project is licensed under the MIT License.



---

Happy rendering!
Mostly generated by gpt-4o.