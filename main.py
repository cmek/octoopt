import asyncio
import os
from dotenv import load_dotenv
from agileocto import OctopusAgile
from telegram.ext import Application

load_dotenv()

async def send_message(bot, group_id, text):
    await bot.send_message(chat_id=group_id, text=text)

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    group_id = os.getenv("TELEGRAM_GROUP_ID")

    api = OctopusAgile(day=0)

    battery_charge_window = api.get_battery_charge_window()
    peak_time_window = api.get_peak_time()

    message = f"""battery charge window: {battery_charge_window['start_time']} - {battery_charge_window['end_time']}
battery charge cost: {battery_charge_window['total_cost']}p (@ {battery_charge_window['avg_cost_per_khw']} p/kWh)

peak time window: {peak_time_window['start_time']} - {peak_time_window['end_time']}
peak time cost: {peak_time_window['total_cost']}p (@ {peak_time_window['avg_cost_per_khw']} p/kWh)
savings: {peak_time_window['total_cost'] - battery_charge_window['total_cost']}p"""

    print(message)

    asyncio.run(send_message(app.bot, group_id, message))

if __name__ == "__main__":
    main()
