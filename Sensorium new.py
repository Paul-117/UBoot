import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import label, center_of_mass

# Set the random seed for reproducibility
np.random.seed(0)

# Define the default grid size and scaling factor
default_grid_size = 100
scaling_factor = 1  # You can set this to any value (including below 1)
grid_size = int(default_grid_size * scaling_factor)

# Define the parameters of Gaussian clusters, scaled according to the grid size
means = [(20 * scaling_factor, 20 * scaling_factor), 
         (70 * scaling_factor, 70 * scaling_factor), 
         (50 * scaling_factor, 20 * scaling_factor)]
std_devs = [3 * scaling_factor, 3 * scaling_factor, 3 * scaling_factor]  # Scaled standard deviations
intensities = [1, 3, 5]  # Intensity of each Gaussian
noise_level = 0.5  # Noise level
threshold = 0.8  # Threshold for heatmap display
size_threshold = 50  # Minimum size of cluster to be considered valid

# Create a coordinate grid for the entire heatmap
x, y = np.meshgrid(np.arange(grid_size), np.arange(grid_size))

# Create a custom colormap that transitions from black to green
custom_cmap = LinearSegmentedColormap.from_list('custom_green', [(0, 'black'), (1, '#32FF32')])

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 12))
heatmap_data = np.zeros((grid_size, grid_size))

# Use the custom colormap where 0 is black and maximum intensity is green
heatmap = ax.imshow(heatmap_data, cmap=custom_cmap, vmin=0, vmax=5)  # Custom colormap with specific range

ax.set_title('Live Heatmap of Gaussian Distributions')
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')

def generate_heatmap_data():
    heatmap_data = np.zeros((grid_size, grid_size))
    for mean, std_dev, intensity in zip(means, std_devs, intensities):
        mu_x, mu_y = mean
        sigma_x = sigma_y = std_dev
        gaussian_values = intensity * np.exp(-((x - mu_x) ** 2 / (2 * sigma_x ** 2) + (y - mu_y) ** 2 / (2 * sigma_y ** 2)))
        heatmap_data += gaussian_values
    noise = noise_level * np.random.random((grid_size, grid_size))
    heatmap_data += noise
    heatmap_data[heatmap_data < threshold] = 0
    return heatmap_data

def find_cluster_centers(heatmap_data):
    # Apply a binary threshold
    binary_mask = heatmap_data > threshold

    # Label connected components
    labeled_array, num_features = label(binary_mask)

    # Calculate the centroid for each cluster, filtering by size threshold
    centroids = []
    for i in range(1, num_features + 1):
        # Get the coordinates of the current cluster
        cluster_mask = labeled_array == i
        cluster_size = np.sum(cluster_mask)
        
        # Only consider clusters larger than the size threshold
        if cluster_size >= size_threshold:
            # Calculate the center of mass (centroid) for valid clusters
            centroid = center_of_mass(heatmap_data, labels=labeled_array, index=i)
            centroids.append(centroid)

    return centroids

def update_display(frame):
    new_data = generate_heatmap_data()
    heatmap.set_array(new_data)

    # Find cluster centers
    centroids = find_cluster_centers(new_data)

    # Clear previous centroids before plotting new ones
    ax.cla()
    ax.imshow(new_data, cmap=custom_cmap, vmin=0, vmax=5)  # Apply custom color mapping
    ax.set_title('Live Heatmap of Gaussian Distributions')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # Plot centroids on the heatmap
    for centroid in centroids:
        ax.plot(centroid[1], centroid[0], 'ro')  # Plot centroids as red circles

    return [heatmap]

# Use FuncAnimation to continuously update the heatmap
ani = FuncAnimation(fig, update_display, frames=None, blit=False, interval=1000)  # Endless animation at 1 FPS

plt.show()
