import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Step 1: Create the dataset (Supervised Learning requires Labels!)
# Input data (Features): Years of Experience
X = np.array([
    [1], [2], [3], [4], [5]
])

# Output data (Labels/Targets): Salary in thousands ($k)
y = np.array([30, 40, 50, 60, 70])

print("Experience (Years):", X.flatten())
print("Salaries ($k):", y)
print("Notice how we provide BOTH the input and the correct answer.\n")

# Step 2: Choose the model
# We use Linear Regression because we are predicting a continuous number (Salary)
model = LinearRegression()

# Step 3: Let the machine learn (Train the model)
print("Training the machine... (Learning the relationship)\n")
model.fit(X, y)

# Step 4: See the results!
print("--- PREDICTIONS ---")
# Let's predict the salary for someone with 6 years and 10 years of experience
new_experiences = np.array([[6], [10]])
predictions = model.predict(new_experiences)

for i in range(len(new_experiences)):
    print(f"Predicted Salary for {new_experiences[i][0]} years: ${predictions[i]:.2f}k")

# Step 5: Visualize the learned relationship
print("\nClose the graph window to finish the program.")

plt.scatter(X, y, color='blue', s=100, label='Actual Data')
# We plot the line using the predictions for the existing X values
plt.plot(X, model.predict(X), color='red', linewidth=3, label='Learned Regression Line')

plt.title("Salary vs. Experience (Supervised Learning)")
plt.xlabel("Years of Experience")
plt.ylabel("Salary ($k)")
plt.legend()
plt.show()