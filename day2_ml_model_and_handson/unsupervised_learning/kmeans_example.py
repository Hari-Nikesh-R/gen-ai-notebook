import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Step 1: Create the dataset (No labels!)
# Imagine we collected data from 9 students: [Hours Playing Games, Exam Marks]
student_data = np.array([
    [5.0, 20], [6.0, 25], [5.5, 22],  # Group A
    [1.0, 90], [0.5, 95], [1.5, 85],  # Group B
    [1.0, 30], [2.0, 35], [1.5, 40]   # Group C
])

print("Student Data (Games vs Marks):\n", student_data)
print("Notice there are no labels. We don't tell the machine who is who.\n")

# Step 2: Choose the model and the number of clusters (K)
# We want to group these students into 3 categories
k = 3
model = KMeans(n_clusters=k, random_state=42, n_init=10)

# Step 3: Let the machine learn (Find the patterns automatically)
print("Training the machine... (Finding clusters)\n")
model.fit(student_data)

# Step 4: See the results!
print("--- RESULTS ---")
labels = model.labels_
centroids = model.cluster_centers_

for i in range(len(student_data)):
    print(f"Student playing {student_data[i][0]}hrs, scoring {student_data[i][1]:.0f} -> Assigned to Group {labels[i]}")

print("\nWhere are the center points (averages) of these groups?")
for i in range(k):
    print(f"Group {i} Center: {centroids[i][0]:.1f} hours, {centroids[i][1]:.1f} marks")

# Step 5: Visualize the clusters in 2D
print("\nClose the graph window to finish the program.")

# Plot the students
plt.scatter(student_data[:, 0], student_data[:, 1], c=labels, cmap='viridis', s=100, edgecolors='black')

# Plot the center points
plt.scatter(centroids[:, 0], centroids[:, 1], color='red', marker='X', s=200, label='Cluster Centers')

plt.title("Student Segmentation (Clustering)")
plt.xlabel("Hours Playing Games")
plt.ylabel("Exam Marks")
plt.legend()
plt.show()
