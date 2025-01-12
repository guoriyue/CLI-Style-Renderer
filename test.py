import re
from typing import List, NamedTuple
from PIL import Image, ImageDraw, ImageFont
import emoji

# Get the emoji dictionary from the emoji library
language_pack = emoji.EMOJI_UNICODE_ENGLISH
EMOJI_UNICODE_REGEX = "|".join(map(re.escape, sorted(language_pack.values(), key=len, reverse=True)))
EMOJI_REGEX = re.compile(f"({EMOJI_UNICODE_REGEX})")


class NodeType:
    TEXT = 0
    EMOJI = 1


class Node(NamedTuple):
    type: NodeType
    content: str


def split_text_into_nodes(text: str) -> List[Node]:
    nodes = []
    for chunk in EMOJI_REGEX.split(text):
        if not chunk:
            continue
        node_type = NodeType.EMOJI if EMOJI_REGEX.match(chunk) else NodeType.TEXT
        nodes.append(Node(node_type, chunk))
    return nodes


def render_text_with_emoji(text: str, font_path: str, emoji_font_path: str, output_path: str):
    # Set up the fonts
    font_size = 40
    text_font = ImageFont.truetype(font_path, font_size)
    emoji_font = ImageFont.truetype(emoji_font_path, font_size)

    # Split text into nodes
    nodes = split_text_into_nodes(text)

    # Calculate image size
    line_height = font_size + 10
    max_width = sum(font_size if node.type == NodeType.EMOJI else text_font.getsize(node.content)[0] for node in nodes)
    img_width = max_width + 20
    img_height = line_height + 20

    # Create the image
    image = Image.new("RGBA", (img_width, img_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Draw each node
    x = 10
    y = 10
    for node in nodes:
        if node.type == NodeType.TEXT:
            draw.text((x, y), node.content, font=text_font, fill="black")
            x += text_font.getsize(node.content)[0]
        elif node.type == NodeType.EMOJI:
            draw.text((x, y), node.content, font=emoji_font, embedded_color=True)
            x += font_size

    # Save the image
    image.save(output_path)


# Example usage
if __name__ == "__main__":
    text = "I 🕴️ 100% 💶 agree 💯"
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Path to text font
    emoji_font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"  # Path to emoji font
    output_path = "output.png"

    render_text_with_emoji(text, font_path, emoji_font_path, output_path)
    print(f"Image saved to {output_path}")
