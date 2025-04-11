from PIL import Image, ImageDraw, ImageFont
import os

def create_math_icon():
    # Create a new image with a transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle
    circle_color = (60, 140, 231)  # #3C8CE7
    draw.ellipse([10, 10, size-10, size-10], fill=circle_color)
    
    # Draw a plus sign
    line_color = (255, 255, 255)
    line_width = 20
    center = size // 2
    # Horizontal line
    draw.line([(center - 50, center), (center + 50, center)], 
              fill=line_color, width=line_width)
    # Vertical line
    draw.line([(center, center - 50), (center, center + 50)], 
              fill=line_color, width=line_width)
    
    # Save the icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_icon.png")
    image.save(icon_path, "PNG")

if __name__ == "__main__":
    create_math_icon() 