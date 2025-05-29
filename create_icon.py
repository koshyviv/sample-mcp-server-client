#!/usr/bin/env python3
"""
Simple script to create a basic icon for MCP Client X
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon():
        # Create a 256x256 image with a dark blue background
        size = 256
        img = Image.new('RGBA', (size, size), (30, 60, 120, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "MCP" text
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw background circle
        circle_margin = 20
        draw.ellipse([circle_margin, circle_margin, size-circle_margin, size-circle_margin], 
                    fill=(50, 100, 200, 255), outline=(255, 255, 255, 255), width=4)
        
        # Draw text
        text = "MCP"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 10
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Draw subtitle
        try:
            small_font = ImageFont.truetype("arial.ttf", 20)
        except:
            small_font = ImageFont.load_default()
            
        subtitle = "Client X"
        bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (size - sub_width) // 2
        sub_y = y + text_height + 10
        
        draw.text((sub_x, sub_y), subtitle, fill=(200, 200, 200, 255), font=small_font)
        
        # Save as ICO file
        img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("✅ Icon created: icon.ico")
        
        # Also save as PNG for reference
        img.save('icon.png', format='PNG')
        print("✅ Icon created: icon.png")
        
    if __name__ == "__main__":
        create_icon()
        
except ImportError:
    print("⚠️ PIL (Pillow) not available. Creating placeholder icon...")
    # Create a simple text file as placeholder
    with open('icon_placeholder.txt', 'w') as f:
        f.write("Icon placeholder - install Pillow and run create_icon.py to generate icon.ico")
    print("📝 Created icon_placeholder.txt - install Pillow to generate actual icon") 