from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_gradient(width, height, start_color, end_color, filename, text=None):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    
    for y in range(height):
        for x in range(width):
            # Diagonal gradient
            p = (x + y) / (width + height)
            mask_data.append(int(255 * p))
            
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    
    if text:
        draw = ImageDraw.Draw(base)
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
            
        # Draw text in center
        # primitive centering
        w = width // 2
        h = height // 2
        draw.text((w, h), text, fill="white", anchor="mm", font=font)

    base.save(filename)
    print(f"Generated {filename}")

def main():
    os.makedirs("static/images", exist_ok=True)
    
    # Hero Image - Blue to Teal
    create_gradient(1920, 1080, (59, 130, 246), (16, 185, 129), "static/images/hero_image.png")
    
    # Feature Image - Soft Blue/Green
    create_gradient(800, 600, (239, 246, 255), (209, 250, 229), "static/images/feature_image.png")
    
    # Slides
    slides = [
        ("Understanding Analysis", (59, 130, 246), (37, 99, 235)), # Blue
        ("Active Lifestyle", (16, 185, 129), (5, 150, 105)), # Green
        ("Clinical Support", (139, 92, 246), (124, 58, 237)), # Purple
        ("Healthy Nutrition", (245, 158, 11), (217, 119, 6))  # Orange
    ]
    
    for i, (txt, c1, c2) in enumerate(slides):
        create_gradient(1080, 720, c1, c2, f"static/images/slide{i+1}.jpg", text=txt)

if __name__ == "__main__":
    main()
