import numpy as np
import matplotlib.pyplot as plt

def random_star(base_radius=10.0, offset_range=(0.0, 5.0), count=1):
    stars = []
    for _ in range(count):
        theta = np.arccos(1 - 2 * np.random.rand())
        phi = 2 * np.pi * np.random.rand()

        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        offset = np.random.uniform(*offset_range)
        r = base_radius + offset

        stars.append((x * r, y * r, z * r, offset, theta, phi))
    return stars

# Generate initial stars
stars = random_star(10, (0, 5), 5)
xs, ys, zs, offsets, thetas, phis = zip(*stars)

# Sphere mesh
u = np.linspace(0, np.pi, 60)
v = np.linspace(0, 2 * np.pi, 60)
u, v = np.meshgrid(u, v)
sphere_x = 10 * np.sin(u) * np.cos(v)
sphere_y = 10 * np.sin(u) * np.sin(v)
sphere_z = 10 * np.cos(u)

# Texture
size = 512
texture = np.zeros((size, size))

uv_coords = []
for (x, y, z, offset, theta, phi) in stars:
    u = phi / (2 * np.pi)
    v = theta / np.pi
    px = int(u * (size-1))
    py = int(v * (size-1))
    uv_coords.append((px, py))
    intensity = offset / 5.0
    texture[py, px] = max(texture[py, px], intensity)

# Plot setup
fig = plt.figure(figsize=(14, 7))

ax3d = fig.add_subplot(121, projection='3d')
ax3d.scatter(xs, ys, zs, s=5, c='white')
ax3d.plot_surface(sphere_x, sphere_y, sphere_z, color='blue', alpha=0.1, linewidth=0)
ax3d.set_facecolor("black")
ax3d.set_xticks([])
ax3d.set_yticks([])
ax3d.set_zticks([])
ax3d.set_box_aspect([1,1,1])

ax2d = fig.add_subplot(122)
ax2d.imshow(texture, cmap='gray', origin='upper')
ax2d.set_title("Equirectangular offset texture")
ax2d.axis("off")

highlight3d = ax3d.scatter([], [], [], s=80, c='red')
highlight2d = ax2d.scatter([], [], s=80, c='red', marker="o")

# --- Interaction ---
def add_star_from_2d(px, py):
    """Convert 2D click to spherical coords and add star."""
    u = px / (size-1)
    v = py / (size-1)
    phi = u * 2 * np.pi
    theta = v * np.pi

    offset = np.random.uniform(0, 5)
    r = 10 + offset

    x = np.sin(theta) * np.cos(phi) * r
    y = np.sin(theta) * np.sin(phi) * r
    z = np.cos(theta) * r

    stars.append((x, y, z, offset, theta, phi))
    uv_coords.append((px, py))
    texture[py, px] = max(texture[py, px], offset / 5.0)

    xs_list, ys_list, zs_list = zip(*[(s[0], s[1], s[2]) for s in stars])
    return xs_list, ys_list, zs_list

def on_click(event):
    snap_radius = 8

    if event.inaxes == ax2d:
        if event.xdata is None or event.ydata is None:
            return
        px, py = int(event.xdata), int(event.ydata)

        # Check if click is near existing star
        dists = [(px - u)**2 + (py - v)**2 for (u, v) in uv_coords]
        idx = int(np.argmin(dists))
        if dists[idx] <= snap_radius**2:
            highlight3d._offsets3d = ([xs[idx]], [ys[idx]], [zs[idx]])
            highlight2d.set_offsets([[uv_coords[idx][0], uv_coords[idx][1]]])
        else:
            # Add new star
            global xs, ys, zs
            xs, ys, zs = add_star_from_2d(px, py)
            ax3d.cla()
            ax3d.plot_surface(sphere_x, sphere_y, sphere_z, color='blue', alpha=0.1, linewidth=0)
            ax3d.scatter(xs, ys, zs, s=5, c='white')
            ax3d.set_facecolor("black")
            ax3d.set_xticks([])
            ax3d.set_yticks([])
            ax3d.set_zticks([])
            ax3d.set_box_aspect([1,1,1])

    fig.canvas.draw_idle()

fig.canvas.mpl_connect("button_press_event", on_click)
plt.show()
