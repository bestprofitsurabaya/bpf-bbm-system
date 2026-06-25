from PIL import Image, ImageDraw, ImageFont
import os

size = 512
img = Image.new('RGB', (size, size), color='#1a237e')
draw = ImageDraw.Draw(img)

# Logo sederhana
draw.rectangle([50, 50, size-50, size-50], outline='white', width=10)
draw.text((size//2-80, size//2-30), "BPF", fill='white', font=None)
draw.text((size//2-60, size//2+30), "BBM", fill='white', font=None)

img.save('static/icon-512.png')
print("Icon generated")
