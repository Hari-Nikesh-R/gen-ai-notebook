import numpy as np
temperature = [20, 22, 25, 27, 30, 31, 29, 35]
icecream_sales = [120, 115, 150, 160, 210, 200, 190, 260]

print("Temperature Data:", temperature)
print("Sales Data:", icecream_sales)

for i in range(len(temperature)):
    print(
        temperature[i],
        "°C ->",
        icecream_sales[i],
        "ice creams sold"
    )

total_temp_change = temperature[-1] - temperature[0]
total_sales_change = icecream_sales[-1] - icecream_sales[0]

slope = total_sales_change / total_temp_change

print("Estimated Slope:", slope)

def predict_sales(temp):
    return slope * temp - 66

prediction = predict_sales(32)

print("Predicted sales for 32°C:", prediction)

test_temperatures = [26, 28, 33]

for temp in test_temperatures:
    predicted = predict_sales(temp)
    print(temp, "°C -> Predicted Sales:", predicted)

for i in range(len(temperature)):
    
    predicted = predict_sales(temperature[i])
    
    actual = icecream_sales[i]
    
    error = actual - predicted

    print(
        "Temp:", temperature[i],
        "| Actual:", actual,
        "| Predicted:", round(predicted, 2),
        "| Error:", round(error, 2)
    )

temperature = [20, 22, 25, 27, 30, 31, 29, 35]
icecream_sales = [120, 115, 150, 160, 210, 200, 190, 260]

n = len(temperature)

mean_temp  = sum(temperature) / n
mean_sales = sum(icecream_sales) / n

numerator   = sum((temperature[i] - mean_temp) * (icecream_sales[i] - mean_sales) for i in range(n))
denominator = sum((temperature[i] - mean_temp) ** 2 for i in range(n))

slope     = numerator / denominator
intercept = mean_sales - slope * mean_temp

print("\n--- MODEL EVALUATION (MANUAL OLS) ---")
print(f"OLS Slope: {slope:.4f} (Each 1°C increase leads to ~{slope:.1f} more ice creams sold)")
print(f"OLS Intercept: {intercept:.4f} (Baseline adjustment)")

def predict_sales(temp):
    return slope * temp + intercept

print("\n--- PREDICTIONS FOR NEW TEMPERATURES ---")
for temp in [26, 28, 32, 33]:
    print(f"At {temp}°C, we expect to sell about {predict_sales(temp):.0f} ice creams.")

errors    = [icecream_sales[i] - predict_sales(temperature[i]) for i in range(n)]
mse       = sum(e**2 for e in errors) / n
rmse      = mse ** 0.5

ss_res    = sum(e**2 for e in errors)
ss_tot    = sum((icecream_sales[i] - mean_sales)**2 for i in range(n))
r_squared = 1 - (ss_res / ss_tot)

print(f"\nMean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} ice creams (average error)")
print(f"Accuracy (R-squared): {r_squared * 100:.2f}% of sales are explained by temperature.")

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

X = np.array(temperature).reshape(-1, 1)
y = np.array(icecream_sales)

model = LinearRegression()
model.fit(X, y)

print("\n--- SKLEARN MODEL RESULTS ---")
print(f"Sklearn Slope: {model.coef_[0]:.4f}")
print(f"Sklearn Intercept: {model.intercept_:.4f}")

y_pred = model.predict(X)
print(f"Sklearn RMSE: {np.sqrt(mean_squared_error(y, y_pred)):.2f} ice creams")
print(f"Sklearn R²: {r2_score(y, y_pred) * 100:.2f}%")

is_weekend = [0, 0, 0, 0, 1, 1, 0, 1]   # 1 = weekend
rainfall_mm = [0, 2, 0, 5, 0, 0, 10, 0]  # mm of rain that day

X_multi = np.column_stack([temperature, is_weekend, rainfall_mm])
model_multi = LinearRegression()
model_multi.fit(X_multi, y)

print("\n--- MULTI-FEATURE MODEL RESULTS ---")
print("Learned Patterns:")
coefs = dict(zip(['temp', 'weekend', 'rainfall'], model_multi.coef_))
print(f"- Temperature effect: {coefs['temp']:+.2f} ice creams per °C")
print(f"- Weekend effect: {coefs['weekend']:+.2f} ice creams on weekends")
print(f"- Rainfall effect: {coefs['rainfall']:+.2f} ice creams per mm of rain")
print(f"Improved Accuracy (R²): {r2_score(y, model_multi.predict(X_multi)) * 100:.2f}%")