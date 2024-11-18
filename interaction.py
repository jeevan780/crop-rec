import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle

# Load the trained model and scaler
with open(r"Crop-Recommendation-System-Using-Machine-Learning\Crop_Recommendation_Model.pkl", 'rb') as model_file:
    rfc = pickle.load(model_file)

with open(r"Crop-Recommendation-System-Using-Machine-Learning\crop_scaler.pkl", 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Load the dataset for price trend analysis
csv_path = r"Crop-Recommendation-System-Using-Machine-Learning\Crop_recommendation_with_price_data1.csv"
data = pd.read_csv(csv_path)

# Define label mapping
label_mapping = {label: idx for idx, label in enumerate(data['label'].unique(), 1)}
reverse_label_mapping = {v: k for k, v in label_mapping.items()}

# Define price trend thresholds
PRICE_THRESHOLD = 8  # 8% increase triggers "SELL"

def recommend_sell_or_hold(crop_name):
    """Recommend whether to SELL or HOLD based on price trends."""
    crop_data = data[data['label'] == crop_name]
    if crop_data.empty:
        print("Sorry, we don't have price data for this crop.")
        return

    avg_price = crop_data['previous_month_avg'].mean()
    daily_price = crop_data['daily_price'].mean()
    price_change = ((daily_price - avg_price) / avg_price) * 100

    print(f"\nCrop: {crop_name}")
    print(f"Daily Price: ₹{daily_price:.2f}")
    print(f"Previous Month Average Price: ₹{avg_price:.2f}")
    print(f"Price Change: {price_change:.2f}%")

    if price_change > PRICE_THRESHOLD:
        print("Recommendation: SELL")
    else:
        print("Recommendation: HOLD")

def recommend_crop(features):
    """Recommend the best crop based on input features."""
    features_scaled = scaler.transform([features])
    predicted_crop_idx = rfc.predict(features_scaled)[0]
    return reverse_label_mapping[predicted_crop_idx]

def user_interaction():
    """Handle user interaction."""
    print("\nWelcome to the Crop Advisory System!")
    print("Options:")
    print("1. Get Growing Conditions Recommendations")
    print("2. Check Price Trends")
    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\nEnter the following details for crop recommendation:")
        try:
            n = float(input("Nitrogen (N): "))
            p = float(input("Phosphorus (P): "))
            k = float(input("Potassium (K): "))
            temperature = float(input("Temperature (°C): "))
            humidity = float(input("Humidity (%): "))
            ph = float(input("pH: "))
            rainfall = float(input("Rainfall (mm): "))
            features = [n, p, k, temperature, humidity, ph, rainfall]
            recommended_crop = recommend_crop(features)
            print(f"\nRecommended Crop: {recommended_crop}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    elif choice == "2":
        crop_name = input("\nEnter the crop name to check price trends: ").strip()
        recommend_sell_or_hold(crop_name)
    else:
        print("Invalid choice. Please restart the program.")

if __name__ == "__main__":
    user_interaction()
