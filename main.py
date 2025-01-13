import json
from renderer import CLIStyleRenderer

if __name__ == "__main__":
    # Load custom styles from JSON
    with open('style_config.json', 'r') as f:
        custom_styles = json.load(f)
        
    # Create with custom styles
    generator = CLIStyleRenderer(style_config=custom_styles)

    # Example usage with different line styles
    lines = [
        ">> 🖥️ System Analysis",
        "$ 🔍 Checking components... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... Super loooooooooong line... End of line 🐻‍❄️",
        "# 📝 This is a comment",
        "! ⚠️Warning: High CPU usage",
        "! 中文 日本語 한국어",
        "@ ℹ️ Info: 8GB RAM available",
        "img_left: https://pbs.twimg.com/ext_tw_video_thumb/1858064790821974016/pu/img/MQU4WFGD8vSyb_A2.jpg",
        "img_center: images/bear_ryan.png",
        ">>> 🚀 Custom style line"
    ]

    # Generate image
    img_base64 = generator.generate_cli_image(
        lines,
        width=2400,
        show_chrome=True
    )

    # Save image
    generator.save_image_by_timestamp(img_base64, "output")
