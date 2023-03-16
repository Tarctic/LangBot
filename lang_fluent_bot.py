import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from environs import Env

env = Env()
env.read_env()

logger = logging.getLogger(__name__)

def echo(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console
    print(f'user: {update.message.from_user.first_name} sent a message')

    if update.message.text:
        context.bot.send_message(
            update.message.chat_id,
            generate_response_gpt3(update.message.text),
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

def generate_response_gpt3(user_message):
    api_key = os.getenv("GPT_API")
    model = "text-davinci-003"
    prompt = (f"User: {user_message}\n"
              f"Chatbot: ")
    response = requests.post(
        f"https://api.openai.com/v1/engines/{model}/completions",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "prompt" : prompt,
            "max_tokens" : 200,
            "temperature": 0.7
        },
    )
    return response.json()["choices"][0]["text"].strip()

def main() -> None:
    api_key = os.getenv("TELEGRAM_API")
    updater = Updater(api_key)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands
    # dispatcher.add_handler(CommandHandler("scream", scream))

    # Echo any message that is not a command
    dispatcher.add_handler(MessageHandler(~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
