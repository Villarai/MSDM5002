import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image


# 加载PNG图像
img = Image.open("C:/Users/user/Desktop/DVD_logo.png")


img = img.resize((103,47))


# 将图像转换为RGBA（如果不是的话）
img = img.convert("RGBA")

# 获取图像数据
data = img.getdata()

# 创建一个新的图像数据列表
new_data = []

# 黑白互换
for item in data:
    # 互换黑色（0, 0, 0）和白色（255, 255, 255）
    if item[0] == 0 and item[1] == 0 and item[2] == 0:  # 黑色
        new_data.append((255, 255, 255, item[3]))  # 变为白色，保持透明度
    elif item[0] == 255 and item[1] == 255 and item[2] == 255:  # 白色
        new_data.append((0, 0, 0, item[3]))  # 变为黑色，保持透明度
    else:
        new_data.append(item)  # 其他颜色保持不变

# 更新图像数据
img.putdata(new_data)
img = np.array(img)


# Set up the figure and axis with figsize and dpi
fig = plt.figure(facecolor='black', figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)  # Add a single subplot
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust margins

# Set up the figure and axis
# fig, ax = plt.subplots(facecolor='black',figsize=(8, 6), dpi=100)
ax.set_xlim(0, 800)  # Width of the screen
ax.set_ylim(0, 600)  # Height of the screen
ax.set_facecolor('black')
# ax.axis('off')  
# Hide axes ticks



# Initial position and velocity
x, y = np.random.rand(2) * [800 - 100, 600 - 75]  # Random starting position
dx, dy = 3, 3  # Velocity in x and y direction

# Function to update the animation
def update(frame):
    global x, y, dx, dy

    # Update position
    x += dx
    y += dy

    # Bounce off the walls
    if x <= 0 or x >= 800 - 103:
        dx *= -1  # Reverse direction
    if y <= 0 or y >= 600 - 47:
        dy *= -1  # Reverse direction

    # Clear the axis and redraw the logo
    ax.clear()
    ax.set_facecolor('black')  # Set the background color to black
    ax.imshow(img, extent=[x, x + 103, y, y + 47])  # Draw the logo
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.axis('off')  # Hide axes ticks

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=1500, interval=1, repeat=False)

# Show the animation
plt.show()