# First you need to:
# pip install pillow

# Import the PIL module
from PIL import Image, ImageDraw

# Load the image file
image = Image.open("sample.jpg")

# Create an ImageDraw object
draw = ImageDraw.Draw(image)

# Define the coordinates and dimensions of the rectangle
# x and y are the top-left corner of the rectangle
# w and h are the width and height of the rectangle
x = 100
y = 100
w = 200
h = 150

# Draw the rectangle with a red outline
draw.rectangle([(x, y), (x + w, y + h)], outline="red")

# Save the new image to file
image.save("sample_with_rectangle.png")
