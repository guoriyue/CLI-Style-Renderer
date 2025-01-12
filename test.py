from PIL import Image, ImageDraw, ImageFont

# Create a blank image
image = Image.new("RGBA", (500, 200), (255, 255, 255, 255))
draw = ImageDraw.Draw(image)

# Set up the font
# font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Path to DejaVuSans.ttf
font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
font = ImageFont.truetype(font_path, size=109)

# Text with emojis
text = "😍👍pp"  # Use emojis directly

# Draw the text
draw.text((0, 0), text, font=font, fill=(0, 0, 0, 255), embedded_color=True)

# Save or show the image
image.show()
image.save("text_with_emoji.png")
