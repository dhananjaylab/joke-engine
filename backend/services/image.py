from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def render_joke_card(joke_text: str, query: str) -> bytes:
    """Render a shareable PNG card with the joke text."""
    # Card dimensions
    width, height = 800, 600
    bg_color = (9, 9, 11)  # zinc-950
    text_color = (250, 250, 250)  # zinc-50
    accent_color = (168, 85, 247)  # purple-500

    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        joke_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        joke_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Draw title
    draw.text((40, 40), f"Topic: {query}", fill=accent_color, font=title_font)

    # Draw joke text (wrapped)
    max_width = width - 80
    lines = []
    words = joke_text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=joke_font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    y = 120
    for line in lines[:8]:  # Max 8 lines
        draw.text((40, y), line, fill=text_color, font=joke_font)
        y += 50

    # Draw footer
    draw.text((40, height - 60), "Giggle — AI Joke Engine", fill=accent_color, font=footer_font)

    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
