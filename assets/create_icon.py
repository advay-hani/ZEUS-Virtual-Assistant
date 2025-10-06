#!/usr/bin/env python3
"""
Script to create Z.E.U.S. application icon
Creates a simple but professional icon for the application
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_zeus_icon():
    """Create a Z.E.U.S. application icon"""
    # Icon sizes to generate
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create the main 256x256 icon
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle - modern blue gradient effect
    center = size // 2
    radius = size // 2 - 10
    
    # Create gradient background
    for i in range(radius):
        alpha = int(255 * (1 - i / radius))
        color = (30, 144, 255, alpha)  # DodgerBlue with gradient
        draw.ellipse([center - radius + i, center - radius + i, 
                     center + radius - i, center + radius - i], 
                    fill=color)
    
    # Main circle background
    draw.ellipse([center - radius, center - radius, 
                 center + radius, center + radius], 
                fill=(30, 144, 255, 255), outline=(0, 100, 200, 255), width=3)
    
    # Draw "Z" letter in the center
    try:
        # Try to use a system font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw the "Z" character
    text = "Z"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = center - text_width // 2
    text_y = center - text_height // 2
    
    # Draw text with shadow effect
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 128), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Save as ICO file with multiple sizes
    icon_path = os.path.join('assets', 'zeus_icon.ico')
    
    # Create images for different sizes
    images = []
    for icon_size in sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Save as ICO
    img.save(icon_path, format='ICO', sizes=[(s, s) for s in sizes])
    
    # Also save as PNG for other uses
    img.save(os.path.join('assets', 'zeus_icon.png'), format='PNG')
    
    print(f"Icon created successfully: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_zeus_icon()