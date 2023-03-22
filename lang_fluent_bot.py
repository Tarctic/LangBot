import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from environs import Env

env = Env()
env.read_env()

logger = logging.getLogger(__name__)

contextAware = False
saver = []

def contextOn(update: Update, context: CallbackContext) -> None:
    """
    This function handles the /contexton command
    """

    global contextAware
    contextAware = True

def contextOff(update: Update, context: CallbackContext) -> None:
    """
    This function handles the /contextoff command
    """

    global contextAware
    contextAware = False


def clear(update: Update, context: CallbackContext) -> None:
    """
    This function handles the /clear command
    """

    global saver
    saver = []

def contexter(userMsg):

    LIMIT = 30

    global saver
    saver.append("User: " + userMsg + "\n")

    saver = saver[-LIMIT:]
    
    return "\n".join(saver)+"Chatbot: "

def gpt(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """
    # Print to console
    print(f'user: {update.message.from_user.username} sent a message')
    # print(update.message.text)
    
    userMsg = update.message.text

    if contextAware:
        gptFeeder = contexter(userMsg)
    else:
        gptFeeder = f"User: {userMsg}\nLangBot: "
    
    reply = generate_response_gpt3(gptFeeder)

    if contextAware:
        global saver
        saver.append("Chatbot: " + reply + "\n")

        # for i in saver:
        #     print(i)

    if update.message.text:
        context.bot.send_message(
            update.message.chat_id,
            reply,
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

def generate_response_gpt3(user_message):
    api_key = os.getenv("GPT_API")
    model = "text-davinci-003"
    prompt = (user_message)
    response = requests.post(
        f"https://api.openai.com/v1/engines/{model}/completions",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "prompt" : prompt,
            "max_tokens" : 200,
            "temperature": 0.7
        },
    )
    reply = response.json()["choices"][0]["text"].strip()
    return reply

def main() -> None:
    api_key = os.getenv("TELEGRAM_API")
    updater = Updater(api_key)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("contexton", contextOn))
    dispatcher.add_handler(CommandHandler("contextoff", contextOff))
    dispatcher.add_handler(CommandHandler("clear", clear))

    # GPT any message that is not a command
    dispatcher.add_handler(MessageHandler(~Filters.command, gpt))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
