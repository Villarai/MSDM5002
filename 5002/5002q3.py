import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Generate data for the spiral
theta = np.linspace(0, 4 * np.pi, 100)  # Angle from 0 to 4*pi
z = np.linspace(-10 * np.pi, 0, 1000)    # z values from -10*pi to 0

# Use theta to define x and y
x = z * np.sin(z)  # x = z * sin(theta)
y = z * np.cos(z)  # y = z * cos(theta)

# Calculate the radius for each point to determine size
radii = np.sqrt(x**2 + y**2)

# Normalize the radii for size mapping
size = 50 * ((radii - radii.min()) / (radii.max() - radii.min()))  # Normalize and scale size

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Normalize z for color mapping
norm = plt.Normalize(z.min(), z.max())
colors = plt.cm.jet(norm(z)[::-1])  # Use the 'jet' colormap and reverse it

# Plot the points with the reversed 'jet' colormap and varying sizes
ax.scatter(x, y, z, c=colors, marker='o', s=size)

# Plot the spiral line in black
ax.plot(x, y, z, color='k')  # 'k' is the color black

# Set labels
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
ax.set_title('3D Spiral Line with Reversed Jet Colors and Varying Point Sizes')

# Set the aspect ratio of the 3D plot
ax.set_box_aspect([1, 1, 1])  # Aspect ratio is 1:1:1

# Draw three concentric circles on the Z=0 plane
circle_radii = [10, 20, 30]  # Radii for the circles
for radius in circle_radii:
    circle_theta = np.linspace(0, 2 * np.pi, 100)  # Angles for the circle
    circle_x = radius * np.cos(circle_theta)  # X coordinates
    circle_y = radius * np.sin(circle_theta)  # Y coordinates
    ax.plot(circle_x, circle_y, zs=5, color='r')  # Plot circles in red at Z=0

# Plot the point at (0, 0, 0)
ax.scatter(0, 0, 5, color='r', s=10)  # Red point at the origin

# Draw a blue line along x = 0, y = 0, z >= 0
z_line = np.linspace(-150, 0, 100)  # Z values for the line
ax.plot(np.zeros_like(z_line), np.zeros_like(z_line), z_line, color='b')  # Blue line

# Add text "spiral arrow" along the blue line
text_position = (0, 0, -75)  # Position the text along the blue line
ax.text(*text_position, "spiral arrow", color='black', fontsize=12, ha='center', va='center', rotation=90)  # Center the text and rotate


# Hide the axes
ax.axis('off')  # Turn off the axes

# Show legend
ax.legend()

# Show the plot
plt.show()