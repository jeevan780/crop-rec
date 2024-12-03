from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
# Example price data
previous_month_avg_prices = {
    "Rice": 1500, "Maize": 1300, "Jute": 1800, "Cotton": 2000,
    "Coconut": 2500, "Papaya": 3000, "Orange": 3500, "Apple": 4000,
    "Muskmelon": 1000, "Watermelon": 1200, "Grapes": 3200, "Mango": 2800,
    "Banana": 1100, "Pomegranate": 3600, "Lentil": 1400, "Blackgram": 1600,
    "Mungbean": 1500, "Mothbeans": 1700, "Pigeonpeas": 1800, 
    "Kidneybeans": 2000, "Chickpea": 2200, "Coffee": 5000
}

daily_avg_prices = {
    "Rice": 1600, "Maize": 1200, "Jute": 1900, "Cotton": 2100,
    "Coconut": 2600, "Papaya": 2900, "Orange": 3400, "Apple": 3900,
    "Muskmelon": 1100, "Watermelon": 1300, "Grapes": 3100, "Mango": 2700,
    "Banana": 1200, "Pomegranate": 3700, "Lentil": 1300, "Blackgram": 1500,
    "Mungbean": 1600, "Mothbeans": 1800, "Pigeonpeas": 1700, 
    "Kidneybeans": 2100, "Chickpea": 2300, "Coffee": 4900
}

# Complete crop requirements data
crop_requirements = {
    "Rice": {"N": 90, "P": 40, "K": 40, "Temperature": 25, "Humidity": 80, "Rainfall": 200},
    "Maize": {"N": 60, "P": 30, "K": 30, "Temperature": 22, "Humidity": 65, "Rainfall": 120},
    "Jute": {"N": 80, "P": 30, "K": 40, "Temperature": 28, "Humidity": 70, "Rainfall": 150},
    "Cotton": {"N": 50, "P": 20, "K": 30, "Temperature": 26, "Humidity": 60, "Rainfall": 80},
    "Coconut": {"N": 120, "P": 50, "K": 150, "Temperature": 27, "Humidity": 75, "Rainfall": 250},
    "Papaya": {"N": 100, "P": 50, "K": 50, "Temperature": 25, "Humidity": 70, "Rainfall": 150},
    "Orange": {"N": 90, "P": 40, "K": 40, "Temperature": 20, "Humidity": 60, "Rainfall": 100},
    "Apple": {"N": 100, "P": 50, "K": 60, "Temperature": 15, "Humidity": 60, "Rainfall": 120},
    "Muskmelon": {"N": 70, "P": 40, "K": 50, "Temperature": 28, "Humidity": 55, "Rainfall": 50},
    "Watermelon": {"N": 60, "P": 30, "K": 30, "Temperature": 30, "Humidity": 60, "Rainfall": 50},
    "Grapes": {"N": 80, "P": 40, "K": 50, "Temperature": 20, "Humidity": 55, "Rainfall": 70},
    "Mango": {"N": 100, "P": 40, "K": 60, "Temperature": 25, "Humidity": 65, "Rainfall": 150},
    "Banana": {"N": 200, "P": 100, "K": 300, "Temperature": 27, "Humidity": 80, "Rainfall": 200},
    "Pomegranate": {"N": 60, "P": 30, "K": 30, "Temperature": 22, "Humidity": 60, "Rainfall": 50},
    "Lentil": {"N": 20, "P": 30, "K": 20, "Temperature": 18, "Humidity": 50, "Rainfall": 40},
    "Blackgram": {"N": 20, "P": 40, "K": 30, "Temperature": 25, "Humidity": 70, "Rainfall": 80},
    "Mungbean": {"N": 30, "P": 40, "K": 30, "Temperature": 28, "Humidity": 60, "Rainfall": 70},
    "Mothbeans": {"N": 40, "P": 20, "K": 30, "Temperature": 26, "Humidity": 55, "Rainfall": 50},
    "Pigeonpeas": {"N": 60, "P": 40, "K": 40, "Temperature": 24, "Humidity": 65, "Rainfall": 100},
    "Kidneybeans": {"N": 50, "P": 30, "K": 40, "Temperature": 20, "Humidity": 55, "Rainfall": 70},
    "Chickpea": {"N": 40, "P": 30, "K": 40, "Temperature": 20, "Humidity": 50, "Rainfall": 40},
    "Coffee": {"N": 100, "P": 50, "K": 100, "Temperature": 22, "Humidity": 70, "Rainfall": 150}
}

# Function to evaluate crop and provide details
def evaluate_crop(crop_name):
    crop_name = crop_name.capitalize()  # Capitalize input to match dictionary keys

    # Check if crop exists in price and requirements data
    if crop_name not in previous_month_avg_prices:
        return f"The crop '{crop_name}' is not in our database. Please try again."
    if crop_name not in crop_requirements:
        return f"The crop '{crop_name}' does not have detailed requirements data available."

    # Price comparison
    prev_price = previous_month_avg_prices[crop_name]
    daily_price = daily_avg_prices[crop_name]
    price_difference = daily_price - prev_price

    if price_difference > 0:
        price_advice = (
            f"The current price of {crop_name} is {daily_price} (Previous month: {prev_price}).\n"
            f"You can sell the crop now for a profit of {price_difference} per unit."
        )
    elif price_difference < 0:
        price_advice = (
            f"The current price of {crop_name} is {daily_price} (Previous month: {prev_price}).\n"
            f"It is better to hold the crop as the price is {abs(price_difference)} per unit lower than last month."
        )
    else:
        price_advice = (
            f"The current price of {crop_name} is {daily_price}, which is the same as the previous month ({prev_price}).\n"
            f"You may decide based on your convenience."
        )

    # Get crop requirements
    requirements = crop_requirements[crop_name]
    requirements_details = (
        f"Here are the general requirements for growing {crop_name}:\n"
        f"- Nitrogen (N): {requirements['N']} kg/ha\n"
        f"- Phosphorus (P): {requirements['P']} kg/ha\n"
        f"- Potassium (K): {requirements['K']} kg/ha\n"
        f"- Temperature: {requirements['Temperature']}°C\n"
        f"- Humidity: {requirements['Humidity']}%\n"
        f"- Rainfall: {requirements['Rainfall']} mm"
    )

    return f"{price_advice}\n\n{requirements_details}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the AgriVision Bot!\n"
        "Send me the name of a crop, and I'll advise whether to sell or hold it based on prices.\n"
        "I will also provide the general requirements for growing the crop."
    )
user_context = {}
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().lower()
    if user_input in ["hi", "hello"]:
        await update.message.reply_text('Hi how may I help you today')
        return
    # Check if the user has entered a crop name previously
    if user_id in user_context and "crop_name" in user_context[user_id]:
        crop_name = user_context[user_id]["crop_name"]

        if user_input in ["market", "farming"]:
            if user_input == "market":
                response = evaluate_crop(crop_name).split("\n\n")[0]  # Extract market data
                await update.message.reply_text(f"📈 Market Data for {crop_name}:\n{response}")
            elif user_input == "farming":
                response = evaluate_crop(crop_name).split("\n\n")[1]  # Extract farming insights
                await update.message.reply_text(f"🌾 Farming Insights for {crop_name}:\n{response}")
            
            # Clear the context after response
            del user_context[user_id]
            await update.message.reply_text("🌟 Anything else I can assist you with? Type another crop name!")
        else:
            await update.message.reply_text(
                "Please reply with either *Market* or *Farming* to get the relevant information!"
            )
        return
    
    # If it's a new crop query, process it
    crop_name = user_input.capitalize()  # Normalize the input
    if crop_name in previous_month_avg_prices:
        user_context[user_id] = {"crop_name": crop_name}  # Store crop name in context
        await update.message.reply_text(
            f"Do you want market data or farming insights for **{crop_name}**?\n"
            "Please reply with *Market* or *Farming*."
        )
    else:
        await update.message.reply_text(
            "I couldn't find that crop in my database. 💡 Please try another crop name."
        )
        #hello

# Main function to run the bot
def main():
    # Replace 'YOUR_TOKEN_HERE' with your bot's API token
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
