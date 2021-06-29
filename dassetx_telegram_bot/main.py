from telegram import ParseMode
from telegram.ext import Updater, Defaults

from dassetx_telegram_bot.bot.handler import (
    DassetxPriceAlertHandler,
)
from dassetx_telegram_bot.config import Config


def main():
    updater = Updater(
        token=Config.TELEGRAM_TOKEN,
        defaults=Defaults(parse_mode=ParseMode.HTML),
    )
    dispatcher = updater.dispatcher
    price_handler = DassetxPriceAlertHandler()

    dispatcher.add_handler(
        'start', price_handler.start_command
    )  # Accessed via /start
    dispatcher.add_handler(
        'alert', price_handler.price_alert
    )  # Accessed via /alert

    updater.start_polling()  # Start the bot

    updater.idle()  # Wait for the script to be stopped, this will stop the bot as well


if __name__ == '__main__':
    Config.check()
    main()
