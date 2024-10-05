import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Create a sample dataset for demonstration
data = {
    'User_Lat': [27.1751, 18.9219, 13.0493, 12.9763],  # Latitude of famous places
    'User_Lon': [78.0421, 72.8346, 80.2824, 77.5929],  # Longitude of famous places
    'Budget': [200, 500, 300, 100],  # Sample budget values
    'Place_Type': ['historical', 'historical', 'beach', 'park'],  # Place types
    'Recommended_Place': ['Taj Mahal', 'Gateway of India', 'Marina Beach', 'Cubbon Park']  # Place names
}

# Create a DataFrame
df = pd.DataFrame(data)

# Encode the categorical 'Place_Type' and 'Recommended_Place' features
label_enc_place_type = LabelEncoder()
label_enc_recommended_place = LabelEncoder()
df['Place_Type_Encoded'] = label_enc_place_type.fit_transform(df['Place_Type'])
df['Recommended_Place_Encoded'] = label_enc_recommended_place.fit_transform(df['Recommended_Place'])

# Define features and target variable
X = df[['User_Lat', 'User_Lon', 'Budget', 'Place_Type_Encoded']]
y = df['Recommended_Place_Encoded']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model and label encoders
joblib.dump((model, label_enc_place_type, label_enc_recommended_place), 'place_recommender.pkl')
print("Model and label encoders saved as 'place_recommender.pkl'")
