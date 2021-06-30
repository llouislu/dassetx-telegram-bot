import logging

from telegram.ext import Updater

from dassetx_telegram_bot.bot.handler import (
    DassetxPriceAlertHandler,
)
from dassetx_telegram_bot.config import Config
from dassetx_telegram_bot.data_provider.dassetx_price_provider import (
    DassetxPriceProvider,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    updater = Updater(token=Config.TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher
    dassetxPriceProvider = DassetxPriceProvider(job_queue=updater.job_queue)

    price_handler = DassetxPriceAlertHandler(
        dassetxPriceProvider=dassetxPriceProvider
    )

    dispatcher.add_handler(
        price_handler.build_handler('start')
    )  # Accessed via /start
    dispatcher.add_handler(
        price_handler.build_handler('alert')
    )  # Accessed via /alert

    dassetxPriceProvider.start()
    price_handler.start()

    updater.start_polling()  # Start the bot
    updater.idle()


if __name__ == '__main__':
    Config.check()
    main()
