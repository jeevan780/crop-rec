from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import pandas as pd
import pickle
import numpy as np
from gtts import gTTS
import io
import os
from dotenv import load_dotenv
import google.generativeai as genai
# Load data and models
csv_file_path = 'Crop_recommendation_with_price_data1.csv'
model_file_path = 'Crop_Recommendation_Model.pkl'
scaler_file_path = 'crop_scaler.pkl'

crop_data = pd.read_csv(csv_file_path)

with open(model_file_path, 'rb') as model_file:
    crop_model = pickle.load(model_file)

with open(scaler_file_path, 'rb') as scaler_file:
    crop_scaler = pickle.load(scaler_file)

# Helper function to get crop farming details
def get_farming_details(crop_name):
    crop_name = crop_name.lower()
    crop_info = crop_data[crop_data['label'] == crop_name]

    if not crop_info.empty:
        avg_N = crop_info['N'].mean()
        avg_P = crop_info['P'].mean()
        avg_K = crop_info['K'].mean()
        avg_temp = crop_info['temperature'].mean()
        avg_humidity = crop_info['humidity'].mean()
        avg_rainfall = crop_info['rainfall'].mean()

        details = (
            f"Farming Details for {crop_name.capitalize()}:\n"
            f"  - Nitrogen (N): {avg_N:.2f}\n"
            f"  - Phosphorus (P): {avg_P:.2f}\n"
            f"  - Potassium (K): {avg_K:.2f}\n"
            f"  - Temperature: {avg_temp:.2f}°C\n"
            f"  - Humidity: {avg_humidity:.2f}%\n"
            f"  - Rainfall: {avg_rainfall:.2f} mm"
        )
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        details= str(details)
        prompt='''translate this to kannnada and i want only kannada translation as reponse and nothing else :'''+details
        response = model.generate_content(prompt)
        print(response.text)
        if response.text:
            return response.text
        return details
        
        # return details
    else:
        return "Sorry, I couldn't find farming details for that crop."

# Helper function to get crop market details
def get_market_details(crop_name):
    crop_name = crop_name.lower()
    crop_info = crop_data[crop_data['label'] == crop_name]

    if not crop_info.empty:
        avg_price = crop_info['daily_price'].mean()
        avg_change = crop_info['price_change_percentage'].mean()

        if avg_change < 1:
            recommendation = 'It is better to hold the crop'
        else:
            recommendation = 'It is better to sell the crop'

        details = (
            f"Market Details for {crop_name.capitalize()}:\n"
            f"  - Average Daily Price: ₹{avg_price:.2f}\n"
            f"  - Average Price Change: {avg_change:.2f}%\n"
            f"  - Recommendation: {recommendation}"
        )
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        # print(details)
        details= str(details)
        prompt='''translate this to kannnada and i want only kannada translation as reponse and nothing else :'''+details
        response = model.generate_content(prompt)
        if response.text:
            # tts = gTTS(text=message, lang='kn')
            # audio_buffer = io.BytesIO()
            # tts.write_to_fp(audio_buffer)
            # audio_buffer.seek(0)

            # Send voice message
            # context.bot.send_voice(
            #     chat_id=update.effective_chat.id,
            #     voice=audio_buffer,
            #     caption=message
            # )
            return response.text
        return details
    else:
        return "Sorry, I couldn't find market details for that crop."

# Start command
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

# Handle crop information with options
async def crop_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop_name = update.message.text.strip().lower()
    context.user_data['crop_name'] = crop_name

    # Generate options for Farming and Market
    keyboard = [
        [
            InlineKeyboardButton("Farming Details", callback_data='farming'),
            InlineKeyboardButton("Market Details", callback_data='market')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Choose an option for {crop_name.capitalize()}:",
        reply_markup=reply_markup
    )

# Handle user selection for details
async def details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    crop_name = context.user_data.get('crop_name', None)

    if not crop_name:
        await query.edit_message_text("Sorry, I couldn't determine the crop. Please try again.")
        return

    if query.data == 'farming':
        response = get_farming_details(crop_name)
    elif query.data == 'market':
        response = get_market_details(crop_name)
    else:
        response = "Invalid option selected."
    
    tts = gTTS(text=response, lang='kn')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # Send voice message
    await context.bot.send_voice(
        chat_id=update.effective_chat.id,
        voice=audio_buffer,
        caption=response
    )
    # await query.edit_message_text(response)

# Main function to set up the bot
def main():
    load_dotenv()
    bot_token = os.getenv('telegram_tocken')
    application = ApplicationBuilder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crop_info))
    application.add_handler(CallbackQueryHandler(details_handler))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
