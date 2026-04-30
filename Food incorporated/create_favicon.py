#!/usr/bin/env python3
"""
Convert Logo.png to favicon.ico using PIL
"""
from PIL import Image
import os

# Define paths
logo_path = os.path.join(os.path.dirname(__file__), "Images", "Logo.png")
favicon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")

# Standard favicon sizes
sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]

try:
    # Open the logo image
    img = Image.open(logo_path)
    
    # Convert RGBA to RGB if needed
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Create resized versions for favicon
    icon_images = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icon_images.append(resized)
    
    # Save as favicon.ico
    icon_images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in icon_images]
    )
    
    print(f"✓ Favicon created successfully: {favicon_path}")
    print(f"  Sizes: {sizes}")
    
except ImportError:
    print("PIL/Pillow not installed. Installing...")
    os.system("pip install Pillow")
    print("\nPlease run this script again.")
except Exception as e:
    print(f"✗ Error creating favicon: {e}")
    print("\nFallback: Using PNG as web favicon")
