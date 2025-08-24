import numpy as np
import matplotlib.pyplot as plt

def random_star(base_radius=10.0, offset_range=(0.0, 5.0), count=1): #this whole line makes no sense but removing it breaks it 
    stars = []
    for _ in range(count):
        theta = np.arccos(1 - 2 * np.random.rand()) # polar angle (0 at north pole, π at south pole). Formula makes distribution have a uniform distribution
        phi = 2 * np.pi * np.random.rand() # azimuth angle (0–2π) 

        # Change to Cartiasan
        x = np.sin(theta) * np.cos(phi) 
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        offset = np.random.uniform(*offset_range)
        r = base_radius + offset

        stars.append((x * r, y * r, z * r, offset, theta, phi)) # Star's Final Cords
    return stars

# Generate stars
stars = random_star(10, (0, 5), 1) # Actual Varibles (baseradius, offset range, count)
xs, ys, zs, offsets, thetas, phis = zip(*stars) #aggregates elements from each iterable based on their index
#takes all the first elements of each tuple and groups them together, all the second elements together, etc.


# Sphere mesh
u = np.linspace(0, np.pi, 60)
v = np.linspace(0, 2 * np.pi, 60)
u, v = np.meshgrid(u, v)
sphere_x = 10 * np.sin(u) * np.cos(v)
sphere_y = 10 * np.sin(u) * np.sin(v)
sphere_z = 10 * np.cos(u)

# --- Texture ---
size = 512
texture = np.zeros((size, size))

uv_coords = []
for (x, y, z, offset, theta, phi) in stars:
    u = phi / (2 * np.pi) #Normalizes Spherical cords to UV cords
    v = theta / np.pi
    px = int(u * (size-1)) # Converts normalized cords to actual pixel cords (size -1) makes the coordinates fit within the texture array
    py = int(v * (size-1)) 
    uv_coords.append((px, py)) #Stores the calculated 2D pixel coordinates

    intensity = offset / 5.0 
    texture[py, px] = max(texture[py, px], intensity) #If two overlapping stars exist take the brighter one

# --- Plot setup ---
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
def on_click(event):
    snap_radius = 8  # pixel radius for snapping

    if event.inaxes == ax2d:  # Click in 2D texture
        if event.xdata is None or event.ydata is None:
            return
        px, py = int(event.xdata), int(event.ydata)

        # find stars within snap radius
        dists = [(px - u)**2 + (py - v)**2 for (u, v) in uv_coords]
        idx = int(np.argmin(dists))
        if dists[idx] > snap_radius**2:
            return  # too far from any star → ignore click

    elif event.inaxes == ax3d:  # Click in 3D plot
        # Project star positions to screen coords
        proj = ax3d.transData.transform(np.vstack([xs, ys]).T)
        px, py = event.x, event.y
        dists = (proj[:,0] - px)**2 + (proj[:,1] - py)**2
        idx = int(np.argmin(dists))
        if dists[idx] > snap_radius**2:
            return  # too far → ignore click
    else:
        return

    # Update highlights
    highlight3d._offsets3d = ([xs[idx]], [ys[idx]], [zs[idx]])
    highlight2d.set_offsets([[uv_coords[idx][0], uv_coords[idx][1]]])
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("button_press_event", on_click)
plt.show()
