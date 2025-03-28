import matplotlib.pyplot as plt
import numpy as np

# Generate fake inertia data to simulate an elbow at 4 clusters
clusters = np.arange(1, 11)
inertia = [170000, 120000, 80000, 30000, 25000, 24000, 23000, 22500, 22000, 21500]  # Example inertia values

plt.figure(figsize=(8, 6))
plt.plot(clusters, inertia, marker='o', linestyle='-', color='b')

# Title and labels
plt.title('Elbow Method for Optimal Clusters', fontsize=14)
plt.xlabel('Number of Clusters', fontsize=12)
plt.ylabel('Inertia', fontsize=12)

# Save the plot
plt.savefig('../frontend/frontend/public/images/markdown/fake_elbow_plot.png')
plt.close()

# Optionally display the plot
# plt.show()
