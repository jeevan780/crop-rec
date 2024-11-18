import logging
import pickle
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load the trained model and scaler
with open(r"Crop-Recommendation-System-Using-Machine-Learning\Crop_Recommendation_Model.pkl", 'rb') as model_file:
    model = pickle.load(model_file)

with open(r"Crop-Recommendation-System-Using-Machine-Learning\crop_scaler.pkl", 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Load dataset for crop names and prices
csv_path = r"Crop-Recommendation-System-Using-Machine-Learning\Crop_recommendation_with_price_data1.csv"
data = pd.read_csv(csv_path)

# Create a mapping for crops and their average prices
crop_prices = data.groupby('label')['average_price'].mean().to_dict()  # Adjust column name if needed
available_crops = set(crop_prices.keys())  # Set of crop names for quick lookup

# Bot Token
TOKEN = '7650084244:AAHW_NvsDywSyRPDXqCyn3ftkB8tZ49hMbY'  # Replace with your actual token

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Welcome to the AgriVision Bot! Use /recommend followed by the crop name to get a price recommendation.\n"
        f"Example: /recommend wheat"
    )

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Verify user input
        if not context.args:
            await update.message.reply_text("Please provide a crop name after /recommend, e.g., /recommend wheat.")
            return

        # Get crop name from user input
        crop_name = " ".join(context.args).strip().lower()
        
        # Check if the crop exists in the dataset
        if crop_name not in available_crops:
            await update.message.reply_text(f"Sorry, I couldn't find any information on '{crop_name}'. Please check the crop name.")
            return

        # Get average price for the crop
        average_price = crop_prices[crop_name]

        # Sample recommendation logic
        if average_price > 100:
            recommendation = "Recommended to sell the crop now!"
        else:
            recommendation = "Hold the crop; the price might improve."

        # Send the recommendation to the user
        await update.message.reply_text(
            f"Crop: {crop_name.capitalize()}\n"
            f"Average Price: {average_price:.2f}\n"
            f"Recommendation: {recommendation}"
        )
    except Exception as e:
        logger.error(f"Error handling recommend command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

# Error Handling
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Update "{update}" caused error "{context.error}"')

# Main Function
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recommend", recommend))

    # Error Handler
    application.add_error_handler(error)

    # Start Bot
    application.run_polling()

if __name__ == '__main__':
    main()
