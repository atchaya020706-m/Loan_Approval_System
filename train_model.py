import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle

# Load Dataset
data = pd.read_csv("loan.csv")

# Input and Output
X = data[["Age", "Income", "LoanAmount", "CreditScore"]]
y = data["Approved"]

# Split Dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Save Model
with open("loan_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model Trained Successfully!")