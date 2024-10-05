import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load your data
data = pd.read_csv('path_to_your_dataset.csv')  # Replace with the path to your dataset

# Preprocess your data
X = data[['age', 'weight', 'height']]  # Example feature columns
y = data['food_recommendation']  # Target column

# Encode categorical variables if needed
le = LabelEncoder()
y = le.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model and label encoder
joblib.dump(model, 'food_recommendation_model.pkl')
joblib.dump(le, 'label_encoder.pkl')
