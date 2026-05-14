# student_marks.py

hours_studied = [1, 2, 3, 4, 5]
marks_scored = [20, 30, 40, 50, 60]

print("Hours Studied:", hours_studied)
print("Marks Scored:", marks_scored)

for i in range(len(hours_studied)):
    print(hours_studied[i], "hours ->", marks_scored[i], "marks")

difference_hours = hours_studied[1] - hours_studied[0]
difference_marks = marks_scored[1] - marks_scored[0]

slope = difference_marks / difference_hours

print("Slope:", slope)

def predict_marks(hours):
    return hours * slope + 10

prediction = predict_marks(6)

print("Prediction for 6 hours:", prediction)