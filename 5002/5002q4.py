from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10, 10), dpi=100)
ax1 = plt.subplot(111, projection='3d', proj_type='ortho')

# plot the target
theta = np.linspace(0, np.pi * 2, 500)
for nr in range(4):
    x = np.sin(theta) * nr * 10
    y = np.cos(theta) * nr * 10
    ax1.scatter3D(x, 5, y, c='r', s=1)

# plot the spiral arrow
Num_period = 10
Num_points = 500
# Data for a three-dimensional line
zline = np.linspace(-np.pi * Num_period, 0, Num_points)
xline = np.sin(zline) * zline
yline = np.cos(zline) * zline

line, = ax1.plot3D(xline, zline, yline, 'gray')
arrow_z = zline * 3
arrow, = ax1.plot3D(xline * 0, arrow_z, yline * 0, linewidth=2, color='b')
scatter = ax1.scatter3D(xline, zline, yline, c=abs(zline), s=abs(zline), cmap='jet')
tail_z = np.linspace(-np.pi * Num_period*3, -np.pi * Num_period*3 - 10, 100)
tail_y = tail_z + np.pi * Num_period*3
tail_x = tail_z * 0
taila, = ax1.plot3D(tail_x, tail_z, tail_y, linewidth=2, color='b')
tailb, = ax1.plot3D(tail_x, tail_z + 4, tail_y, linewidth=2, color='b')
tailc, = ax1.plot3D(tail_x, tail_z + 8, tail_y, linewidth=2, color='b')
taild, = ax1.plot3D(tail_x, tail_z, -tail_y, linewidth=2, color='b')
taile, = ax1.plot3D(tail_x, tail_z + 4, -tail_y, linewidth=2, color='b')
tailf, = ax1.plot3D(tail_x, tail_z + 8, -tail_y, linewidth=2, color='b')

# Animation parameters
num_frames = 20
rotation_speed = 0.25
move_speed = 0.25
target_z = 5  # Target z position to move towards


word_z = -70
word = ax1.text(0,word_z,2,'spiral arrow',fontsize=20)
phi = 0
theta = -15
ax1.view_init(phi, theta)

ax1.set_box_aspect([1, 5, 1])

plt.axis('off')

for frame in range(num_frames):
    # Update the line position
    word_z += move_speed
    tail_z += move_speed
    arrow_z += move_speed
    zline += move_speed  # Move towards the target
    # Rotate around the z-axis
    angle = -rotation_speed * frame
    xline_rotated = xline * np.cos(angle) - yline * np.sin(angle)
    yline_rotated = xline * np.sin(angle) + yline * np.cos(angle)
    tail_x_rotated = tail_x + tail_y * np.sin(-angle)
    tail_y_rotated = tail_y * np.cos(-angle)


    #scatter = ax1.scatter3D(xline_rotated, zline, yline_rotated, c=abs(zline), s=abs(zline), cmap='jet')

    # Update the plot
    line.set_data(xline_rotated, zline)
    line.set_3d_properties(yline_rotated)

    taila.set_data(tail_x_rotated, tail_z)
    taila.set_3d_properties(tail_y_rotated)
    tailb.set_data(tail_x_rotated, tail_z+4)
    tailb.set_3d_properties(tail_y_rotated)
    tailc.set_data(tail_x_rotated, tail_z+8)
    tailc.set_3d_properties(tail_y_rotated)

    taild.set_data(-tail_x_rotated, tail_z)
    taild.set_3d_properties(-tail_y_rotated)
    taile.set_data(-tail_x_rotated, tail_z+4)
    taile.set_3d_properties(-tail_y_rotated)
    tailf.set_data(-tail_x_rotated, tail_z+8)
    tailf.set_3d_properties(-tail_y_rotated)
    

    scatter._offsets3d = (xline_rotated, zline, yline_rotated)
    
    arrow.set_data(xline_rotated * 0, arrow_z)  # xline_rotated * 0 to keep it vertical
    arrow.set_3d_properties(yline_rotated * 0)  # Keep the y position zero

    word.set_position((0, word_z, 2))  # 更新word的位置

    if frame == num_frames - 1:
        ax1.text(0, 5, 35, 'Hit the target', fontsize=20, horizontalalignment = 'center')

    # Redraw the figure
    plt.pause(0.05)

# phi = 0
# theta = -15
# ax1.view_init(phi, theta)

#ax1.text(0, 0, 35, 'Hit the target', fontsize=20)
# ensure the aspect is correct
# ax1.set_box_aspect([1, 5, 1])

# plt.axis('off')
plt.show()