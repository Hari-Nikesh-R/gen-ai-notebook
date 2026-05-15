from sklearn.linear_model import LogisticRegression
import numpy as np

# Input data: Study Hours (Feature)
# ML models expect data in a 2D array format
X = np.array([[1], [2], [3], [5]])

# Output labels: 0 = Fail, 1 = Pass (Labels)
y = np.array([0, 0, 1, 1])

# 1. Create the model (Logistic Regression for classification)
model = LogisticRegression()

# 2. Train the model (The model learns the relationship)
model.fit(X, y)

# 3. Predict for a new student (4 hours of study)
prediction = model.predict([[4]])

print(f"Prediction for 4 hours: {'Pass' if prediction[0] == 1 else 'Fail'}")