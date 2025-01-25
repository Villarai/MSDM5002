import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import colorsys  # Import colorsys for HSV to RGB conversion

# Load PNG image
img = Image.open("C:/Users/user/Desktop/DVD_logo.png")
img = img.resize((103, 47))

# Convert image to RGBA
img = img.convert("RGBA")

# Get image data
data = img.getdata()

# Create a new image data list
new_data = []

# Black and white swap
for item in data:
    if item[0] == 0 and item[1] == 0 and item[2] == 0:  # Black
        new_data.append((255, 255, 255, item[3]))  # Change to white
    elif item[0] == 255 and item[1] == 255 and item[2] == 255:  # White
        new_data.append((0, 0, 0, item[3]))  # Change to black
    else:
        new_data.append(item)  # Keep other colors

# Update image data
img.putdata(new_data)
img = np.array(img)

# Set up the figure and axis
fig = plt.figure(facecolor='black', figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)  # Add a single subplot
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust margins

# Set up the axis limits
ax.set_xlim(0, 800)
ax.set_ylim(0, 600)
ax.set_facecolor('black')
ax.axis('off')  # Hide axes ticks

# Initial position and velocity
x, y = np.random.rand(2) * [800 - 103, 600 - 47]  # Random starting position
dx, dy = 3, 3  # Velocity in x and y direction

# Set a fixed initial color (e.g., white)
current_color = (1, 1, 1)  # RGB color (white)

# Function to generate a random color in RGB from HSV
def random_color():
    hue = np.random.rand()
    saturation = 1.0  # Full saturation
    value = 1.0      # Full brightness
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (r, g, b)

# Function to update the animation
def update(frame):
    global x, y, dx, dy, current_color

    # Update position
    x += dx
    y += dy

    # Bounce off the walls
    if x <= 0 or x >= 800 - 103:
        dx *= -1  # Reverse direction
        current_color = random_color()  # Change color
    if y <= 0 or y >= 600 - 47:
        dy *= -1  # Reverse direction
        current_color = random_color()  # Change color

    # Create a colored version of the logo
    colored_img = img.copy()
    for i in range(colored_img.shape[0]):
        for j in range(colored_img.shape[1]):
            if colored_img[i, j, 3] > 0:  # Only modify non-transparent pixels
                colored_img[i, j, 0] = int(current_color[0] * 255)  # Red
                colored_img[i, j, 1] = int(current_color[1] * 255)  # Green
                colored_img[i, j, 2] = int(current_color[2] * 255)  # Blue

    # Clear the axis and redraw the logo
    ax.clear()
    ax.set_facecolor('black')  # Set the background color to black
    ax.imshow(colored_img, extent=[x, x + 103, y, y + 47])  # Draw the logo
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.axis('off')  # Hide axes ticks

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=1500, interval=1, repeat=False)

# Show the animation
plt.show()