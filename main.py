import asyncio
import os
import logging
import argparse
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
    parser = argparse.ArgumentParser(
        description="Octopus Agile + GivEnergy automation script"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without making changes or sending messages",
    )
    parser.add_argument(
        "--day",
        type=int,
        default=1,
        help="Day to apply settings for: 0=today, 1=tomorrow (default), etc.",
    )
    args = parser.parse_args()

    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    group_id = os.getenv("TELEGRAM_GROUP_ID")
    giveapi = GivEnergyApi(
        os.getenv("GIVENERGY_API_KEY"), os.getenv("INVERTER_SERIAL_NUMBER")
    )

    # 0 means get data for today
    # by default it's set to 1 but that will only work if run after 8pm
    # since ocotopus publish pricing data between 4 and 8pm.
    api = OctopusAgile(
        product_code=OCTOPUS_PRODUCT_CODE, tariff_code=OCTOPUS_TARIFF_CODE, day=args.day
    )

    battery_charge_window = api.get_battery_charge_window()
    peak_time_window = api.get_peak_time(slots=1)
    savings = peak_time_window["total_cost"] - battery_charge_window["total_cost"]

    message = f"""battery charge window: {battery_charge_window["start_time"]} - {battery_charge_window["end_time"]} {battery_charge_window["start_time_hour"]} - {battery_charge_window["end_time_hour"]}
battery charge cost: {battery_charge_window["total_cost"]:.3f}p (@ {battery_charge_window["avg_cost_per_khw"]:.3f} p/kWh)

peak time window: {peak_time_window["start_time"]} - {peak_time_window["end_time"]} {peak_time_window["start_time_hour"]} - {peak_time_window["end_time_hour"]}
peak time cost: {peak_time_window["total_cost"]:.3f}p (@ {peak_time_window["avg_cost_per_khw"]:.3f} p/kWh)
savings: {savings:.3f}p"""
    print(message)

    if args.dry_run:
        print("DRY RUN: The following inverter settings would be applied:")
        print(f"DC Discharge 1 Start Time: {peak_time_window['start_time_hour']}")
        print(f"DC Discharge 1 End Time: {peak_time_window['end_time_hour']}")
        print(f"AC Charge 1 Start Time: {battery_charge_window['start_time_hour']}")
        print(f"AC Charge 1 End Time: {battery_charge_window['end_time_hour']}")
        print(f"Pause Battery Start Time: {battery_charge_window['end_time_hour']}")
        print(f"Pause Battery End Time: {peak_time_window['start_time_hour']}")
    else:
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

        asyncio.run(send_message(app.bot, group_id, message))


if __name__ == "__main__":
    main()
