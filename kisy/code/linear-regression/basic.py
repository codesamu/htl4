import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

# Step 1: Load existing CSV
weather_data_distributed = pd.read_csv("weather.csv")

# Step 2: Plot the data
colors = {'Rain': 'blue', 'No Rain': 'red'}
plt.scatter(weather_data_distributed["Humidity (%)"], 
            weather_data_distributed["Pressure (mb)"], 
            c=weather_data_distributed["Rain"].map(colors), alpha=0.7)
plt.xlabel('Humidity (%)')
plt.ylabel('Pressure (mb)')
plt.title('Distributed Weather Data: Rain vs No Rain')

# Step 3: Use Logistic Regression for a separating line
# Convert labels to 0 (No Rain) and 1 (Rain)
y_distributed = np.array([1 if label == "Rain" else 0 for label in weather_data_distributed["Rain"]])
X_distributed = weather_data_distributed[["Humidity (%)", "Pressure (mb)"]]

# Fit the Logistic Regression model
log_reg_distributed = LogisticRegression()
log_reg_distributed.fit(X_distributed, y_distributed)

# Step 4: Plot the separating line
x_values_distributed = np.linspace(30, 100, 100)
y_values_distributed = -(log_reg_distributed.coef_[0][0] * x_values_distributed + 
                         log_reg_distributed.intercept_[0]) / log_reg_distributed.coef_[0][1]

plt.plot(x_values_distributed, y_values_distributed, color='green', label='Logistic Regression Line')

#User
h= float(input("Enter Humidity in %"))
p= float(input("Enter pressure in mb"))
pred=log_reg_distributed.predict([[h,p]])

label="Rain" if pred == 1 else "No Rain"
print(f"Prediction: {label}")

plt.scatter(h,p,color="lime",s=150,marker="*", label=f"Your Input: {label}")

plt.legend()
plt.show()
