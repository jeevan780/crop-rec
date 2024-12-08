from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import pickle
import numpy as np
from gtts import gTTS
import io
from dotenv import load_dotenv
import os



# Load data and models
csv_file_path = 'Crop_recommendation_with_price_data1.csv'
model_file_path = 'Crop_Recommendation_Model.pkl'
scaler_file_path = 'crop_scaler.pkl'
load_dotenv('.env')

crop_data = pd.read_csv(csv_file_path)

with open(model_file_path, 'rb') as model_file:
    crop_model = pickle.load(model_file)

with open(scaler_file_path, 'rb') as scaler_file:
    crop_scaler = pickle.load(scaler_file)

# Helper function to get crop details
def get_crop_description(crop_name):
    crop_name = crop_name.lower()
    crop_info = crop_data[crop_data['label'] == crop_name]
    
    if not crop_info.empty:
        # Extract average conditions and price info
        avg_N = crop_info['N'].mean()
        avg_P = crop_info['P'].mean()
        avg_K = crop_info['K'].mean()
        avg_temp = crop_info['temperature'].mean()
        avg_humidity = crop_info['humidity'].mean()
        avg_rainfall = crop_info['rainfall'].mean()
        avg_price = crop_info['daily_price'].mean()
        avg_change = crop_info['price_change_percentage'].mean()

        if avg_change < 1:
            recommendation = 'It is better to hold the crop'
        else:
            recommendation = 'It is better to sold the crop'
        
        description = (
            f"Crop: {crop_name.capitalize()}\n"
            f"Average Conditions:\n"
            f"  - Nitrogen (N): {avg_N:.2f}\n"
            f"  - Phosphorus (P): {avg_P:.2f}\n"
            f"  - Potassium (K): {avg_K:.2f}\n"
            f"  - Temperature: {avg_temp:.2f}°C\n"
            f"  - Humidity: {avg_humidity:.2f}%\n"
            f"  - Rainfall: {avg_rainfall:.2f} mm\n"
            f"Price Information:\n"
            f"  - Average Daily Price: ₹{avg_price:.2f}\n"
            f"  - Average Price Change: {avg_change:.2f}%\n"
            f"Recommendation: {recommendation}\n"
        )
        return description
    else:
        return "Sorry, I couldn't find any information about that crop. Please check the spelling or try another crop."

# Helper function to predict crop suitability
def predict_crop_suitability(N, P, K, temperature, humidity, ph, rainfall):
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    scaled_data = crop_scaler.transform(input_data)
    prediction = crop_model.predict(scaled_data)
    return prediction[0]

# Define bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "ಅಗ್ರಿವಿಷನ್ ಸ್ವಾಗತ! ಬೆಳೆ ಹೆಸರನ್ನು ಕಳುಹಿಸಿ, ಬೆಲೆ ಆಧಾರಿತ ಸಲಹೆ ಪಡೆಯಿರಿ."

    # Generate speech from text
    tts = gTTS(text=message, lang='kn')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # Send voice message
    await context.bot.send_voice(
        chat_id=update.effective_chat.id,
        voice=audio_buffer,
        caption=message
    )
    await update.message.reply_text(
        "Welcome to the Crop Info Bot! Enter a crop name to get its details\n"
        "The available crops in our BOt are\n"
        "Rice\n"
        "Maize\n"
        "Jute\n"
        "Cotton\n"
        "Coconut\n"
        "Papaya\n"
        "Orange\n"
        "Apple\n"
        "Muskmelon\n"
        "Watermelon\n"
        "Grapes\n"
        "Mango\n"
        "Banana\n"
        "Pomegranate\n"
        "Lentil\n"
        "Blackgram\n"
        "Mungbean\n"
        "Mothbeans\n"
        "Pigeonpeas\n"
        "Kidneybeans\n"
        "Coffee\n"
    )


async def crop_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    if '=' in user_message:  # If user provides conditions for prediction
        try:
            # Parse user input
            conditions = dict(item.split('=') for item in user_message.split(','))
            N = float(conditions['N'])
            P = float(conditions['P'])
            K = float(conditions['K'])
            temperature = float(conditions['T'])
            humidity = float(conditions['H'])
            ph = float(conditions['pH'])
            rainfall = float(conditions['R'])
            
            # Predict crop
            predicted_crop = predict_crop_suitability(N, P, K, temperature, humidity, ph, rainfall)
            response = f"Based on the provided conditions, the recommended crop is: {predicted_crop.capitalize()}."
        except (ValueError, KeyError):
            response = "Invalid input format. Please use the format: N=90,P=42,K=43,T=25,H=80,pH=6.5,R=200"
    else:  # Otherwise, fetch crop details
        response = get_crop_description(user_message)
    
    await update.message.reply_text(response)

# Main function to set up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot's API token
    
    application = ApplicationBuilder().token(os.getenv('telegram_tocken')).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crop_info))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
