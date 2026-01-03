import asyncio
import os
import logging
from dotenv import load_dotenv
from agileocto import OctopusAgile
from telegram.ext import Application
from givenergy import GivEnergyApi
import json
from datetime import datetime, timedelta
from octoapi import OctoApi

OCTOPUS_PRODUCT_CODE = "AGILE-24-10-01"
OCTOPUS_TARIFF_CODE = "E-1R-AGILE-24-10-01-G"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


async def send_message(bot, group_id, text):
    await bot.send_message(chat_id=group_id, text=text)


def main():
    old_octopus_rate = 27.0

    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    group_id = os.getenv("TELEGRAM_GROUP_ID")

    # 0 means get data for today
    # by default it's set to 1 but that will only work if run after 8pm
    # since ocotopus publish pricing data between 4 and 8pm.
    api = OctopusAgile(
        product_code=OCTOPUS_PRODUCT_CODE, tariff_code=OCTOPUS_TARIFF_CODE, day=-2
    )

    price_data = api.get_input_data(day=-2)

    octo_api = OctoApi(os.getenv("OCTOPUS_API_KEY"))
    # octo_api.getConsumption(os.getenv("OCTOPUS_MPAN"), os.getenv("OCTOPUS_SERIAL_NUMBER"), day=-2))

    consumption_data = octo_api.getConsumption(
        os.getenv("OCTOPUS_MPAN"), os.getenv("OCTOPUS_SERIAL_NUMBER"), day=-2
    ).get("results")

    price_lookup = {p["valid_from"]: p["value_inc_vat"] for p in price_data}

    total_power_kwh = 0
    total_cost = 0

    for entry in consumption_data:
        start = entry["interval_start"]
        consumption = entry["consumption"]  # in kWh
        price = price_lookup.get(start)
        if price is not None:
            cost = consumption * price
            total_power_kwh += consumption
            total_cost += cost
            print(
                f"{start}: {consumption} kWh, Price: {price} p/kWh, Cost: {cost:.3f} p"
            )
        else:
            print(f"{start}: No price data")

    message = f"total power usage: {total_power_kwh} kWh, total cost: {total_cost / 100:.3f} £, old tariff: {(total_power_kwh * old_octopus_rate) / 100:.3f}"
    print(message)

    asyncio.run(send_message(app.bot, group_id, message))


if __name__ == "__main__":
    main()
