import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

df = pd.read_csv('hotel_final_cleaned.csv')

selected_features = [
    'hotel', 'lead_time', 'arrival_date_month', 'arrival_date_day_of_month',
    'total_stay', 'market_segment', 'country', 'previous_cancellations',
    'booking_changes', 'total_of_special_requests', 'adr'
]

X = df[selected_features].copy()
y = df['is_canceled']

categorical_cols = ['hotel', 'arrival_date_month', 'market_segment', 'country']
encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")

with open('rf_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)

with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
