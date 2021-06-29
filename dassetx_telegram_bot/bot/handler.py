from dassetx_telegram_bot.data_provider.dassetx_price_provider import (
    DassetxPriceProvider,
    DassetxPrice,
)


class DassetxPriceAlertHandler:
    def __init__(self):
        self._price_provider = DassetxPriceProvider()

    def start_command(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Hello there! I\'m Dassetx bot NON-OFFICIAL.',
        )

    def price_alert(self, update, context):
        if len(context.args) < 2:
            # invalid arguments
            # print help
            response = (
                '⚠️ Please provide a crypto code and a price value: \n'
                '<i>/price_alert {crypto code} {> / &lt;} {price}</i>'
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=response
            )
            return

        crypto = context.args[0].upper()
        sign = context.args[1]
        price = context.args[2]

        context.job_queue.run_repeating(
            self._monitor_price,
            interval=15,
            first=15,
            context=[crypto, sign, price, update.message.chat_id],
        )

        response = (
            f"⏳ I will send you a message when the price of {crypto}"
            f"reaches ${price}, \n"
        )
        response += (
            f"the current price of {crypto} is NZ$"
            # TODO: check if it's None if property 'lastTradeRate' not exists
            f"{self._price_provider.get(crypto).lastTradeRate}"
        )
        chat_id = update.effective_chat.id, text = response

    def _make_symbol(self, crypto: str, to="NZD"):
        return f"{crypto}-{to}"

    def _monitor_price(self, context):
        crypto = context.job.context[0]
        sign = context.job.context[1]
        expected_price = context.job.context[2]
        chat_id = context.job.context[3]

        current_tick: DassetxPrice = self._price_provider.get(crypto)
        current_price = current_tick.lastTradeRate

        needs_sending = False
        if sign == "<":
            if current_price < expected_price:
                needs_sending = True
        if sign == ">":
            if current_price > expected_price:
                needs_sending = True

        if needs_sending:
            response = f'👋 {crypto} has surpassed ${expected_price} and has just reached <b>${current_price}</b>!'

            context.job.schedule_removal()

            context.bot.send_message(chat_id=chat_id, text=response)
