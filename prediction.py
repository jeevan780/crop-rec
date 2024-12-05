import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import pickle

# Load dataset
csv_path = r"Crop_recommendation_with_price_data1.csv"  # Replace with your dataset path
data = pd.read_csv(csv_path)

# Prepare features (X) and target (y)
X = data.drop('label', axis=1)
y = data['label']

# Encode target variable
label_mapping = {label: idx for idx, label in enumerate(y.unique(), 1)}
y_encoded = y.map(label_mapping)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Normalize features
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train RandomForestClassifier
rfc = RandomForestClassifier(random_state=42)
rfc.fit(X_train_scaled, y_train)

# Save the model and scaler
with open(r"Crop_Recommendation_Model.pkl", 'wb') as model_file:
    pickle.dump(rfc, model_file)

with open(r"crop_scaler.pkl", 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

# Extract price trends directly from the dataset
if "daily_price" in data.columns and "previous_month_avg" in data.columns:
    # Calculate price trends for each crop
    data["price_change"] = ((data["daily_price"] - data["previous_month_avg"]) / data["previous_month_avg"]) * 100
    price_data = (
        data.groupby("label")[["daily_price", "previous_month_avg", "price_change"]]
        .mean()
        .to_dict(orient="index")
    )
else:
    print("Dataset does not include 'daily_price' or 'previous_month_avg' columns. Add them to enable price trends functionality.")
    price_data = {}

# Recommendation thresholds
PRICE_THRESHOLD = 8  # 8% increase triggers "sell"

def recommend_sell_or_hold(crop_name):
    if crop_name not in price_data:
        print("Sorry, we don't have price data for this crop.")
        return

    daily_price = price_data[crop_name]["daily_price"]
    previous_month_avg = price_data[crop_name]["previous_month_avg"]
    price_change = price_data[crop_name]["price_change"]

    print(f"\nCurrent Daily Price of {crop_name}: ₹{daily_price:.2f}")
    print(f"Previous Month Average Price of {crop_name}: ₹{previous_month_avg:.2f}")
    print(f"Price Change: {price_change:.2f}%")

    if price_change > PRICE_THRESHOLD:
        print("Recommendation: SELL")
    else:
        print("Recommendation: HOLD")

# User interaction function
def user_interaction():
    print("\nWelcome to the Crop Recommendation and Price Advisory System!")
    user_input = input("Do you want to know about growing conditions or price trends? (Enter 'conditions' or 'price'): ").strip().lower()

    if user_input == "conditions":
        try:
            print("\nEnter the following details for growing conditions analysis:")
            n = float(input("Nitrogen (N): "))
            p = float(input("Phosphorus (P): "))
            k = float(input("Potassium (K): "))
            humidity = float(input("Humidity (%): "))
            temperature = float(input("Temperature (°C): "))

            # Combine inputs into feature format
            user_features = [[n, p, k, humidity, temperature]]
            user_features_scaled = scaler.transform(user_features)
            predicted_crop = rfc.predict(user_features_scaled)
            crop_label = {v: k for k, v in label_mapping.items()}[predicted_crop[0]]

            print(f"\nRecommended Crop: {crop_label}")
        except Exception as e:
            print(f"Error in analyzing growing conditions: {e}")

    elif user_input == "price":
        crop_name = input("Enter the crop name to check price trends: ").strip().capitalize()
        recommend_sell_or_hold(crop_name)

    else:
        print("\nInvalid choice. Please restart and enter either 'conditions' or 'price'.")

# Run user interaction
if __name__ == "_main_":
    user_interaction()