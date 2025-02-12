from PIL import Image, ImageDraw, ImageFont
import os

def create_strategy_placeholder(name, size=(120, 120), bg_color="#2c3e50", text_color="#ecf0f1"):
    """Create a placeholder image for a strategy"""
    # Create directory if it doesn't exist
    os.makedirs("images/strategies", exist_ok=True)
    
    # Create image with background
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add strategy name
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Center text
    text = name.split()[0]  # Use first word only
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save image
    filename = f"images/strategies/{name.lower().replace(' ', '_')}.png"
    image.save(filename)
    return filename

def create_all_placeholders():
    """Create placeholder images for all strategies"""
    strategies = [
        'Trend Following',
        'Mean Reversion',
        'Breakout',
        'Scalping'
    ]
    
    for strategy in strategies:
        create_strategy_placeholder(strategy)
    
    # Create generic placeholder
    create_strategy_placeholder('placeholder')

if __name__ == "__main__":
    create_all_placeholders()
    print("Placeholder images created in images/strategies/") 