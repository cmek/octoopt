import asyncio
import os
import logging
from dotenv import load_dotenv
from agileocto import OctopusAgile
from telegram.ext import Application
from givenergy import GivEnergyApi

OCTOPUS_PRODUCT_CODE = "AGILE-24-10-01"
OCTOPUS_TARIFF_CODE = "E-1R-AGILE-24-10-01-G"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


async def send_message(bot, group_id, text):
    await bot.send_message(chat_id=group_id, text=text)


def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    group_id = os.getenv("TELEGRAM_GROUP_ID")
    giveapi = GivEnergyApi(
        os.getenv("GIVENERGY_API_KEY"), os.getenv("INVERTER_SERIAL_NUMBER")
    )

    # 0 means get data for today
    # by default it's set to 1 but that will only work if run after 8pm
    # since ocotopus publish pricing data between 4 and 8pm.
    api = OctopusAgile(
        product_code=OCTOPUS_PRODUCT_CODE, tariff_code=OCTOPUS_TARIFF_CODE, day=1
    )

    battery_charge_window = api.get_battery_charge_window()
    peak_time_window = api.get_peak_time(slots=1)

    message = f"""battery charge window: {battery_charge_window["start_time"]} - {battery_charge_window["end_time"]} {battery_charge_window["start_time_hour"]} - {battery_charge_window["end_time_hour"]}
battery charge cost: {battery_charge_window["total_cost"]}p (@ {battery_charge_window["avg_cost_per_khw"]} p/kWh)

peak time window: {peak_time_window["start_time"]} - {peak_time_window["end_time"]} {peak_time_window["start_time_hour"]} - {peak_time_window["end_time_hour"]}
peak time cost: {peak_time_window["total_cost"]}p (@ {peak_time_window["avg_cost_per_khw"]} p/kWh)
savings: {peak_time_window["total_cost"] - battery_charge_window["total_cost"]}p"""

    # set inverter stuff
    giveapi.writeInverterSetting(
        "DC Discharge 1 Start Time", peak_time_window["start_time_hour"]
    )
    giveapi.writeInverterSetting(
        "DC Discharge 1 End Time", peak_time_window["end_time_hour"]
    )
    giveapi.writeInverterSetting(
        "AC Charge 1 Start Time", battery_charge_window["start_time_hour"]
    )
    giveapi.writeInverterSetting(
        "AC Charge 1 End Time", battery_charge_window["end_time_hour"]
    )
    giveapi.writeInverterSetting(
        "Pause Battery Start Time", battery_charge_window["end_time_hour"]
    )
    # giveapi.writeInverterSetting("Pause Battery End Time", battery_charge_window['start_time_hour'])
    giveapi.writeInverterSetting(
        "Pause Battery End Time", peak_time_window["start_time_hour"]
    )
    print(message)

    asyncio.run(send_message(app.bot, group_id, message))


if __name__ == "__main__":
    main()
